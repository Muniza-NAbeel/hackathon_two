"""Task service with CRUD operations and ownership enforcement."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import (
    SortOrder,
    TaskCreate,
    TaskListResponse,
    TaskRead,
    TaskSortBy,
    TaskStatus,
    TaskUpdate,
)


async def create_task(
    session: AsyncSession,
    user_id: UUID,
    task_data: TaskCreate,
) -> Task:
    """Create a new task for a user."""
    # Strip timezone info to match database timezone-naive datetimes
    due_date = task_data.due_date.replace(tzinfo=None) if task_data.due_date else None

    task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        due_date=due_date,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return task


async def get_tasks(
    session: AsyncSession,
    user_id: UUID,
    status_filter: TaskStatus = TaskStatus.ALL,
    sort_by: TaskSortBy = TaskSortBy.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    page: int = 1,
    per_page: int = 50,
) -> TaskListResponse:
    """
    Get paginated list of tasks for a user with filtering and sorting.

    Args:
        session: Database session
        user_id: Owner's user ID
        status_filter: Filter by completion status (all, pending, completed)
        sort_by: Sort field (title, created_at, due_date)
        sort_order: Sort direction (asc, desc)
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
    """
    # Ensure per_page is within bounds
    per_page = min(max(per_page, 1), 100)
    page = max(page, 1)

    # Base query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status_filter == TaskStatus.PENDING:
        query = query.where(Task.completed == False)  # noqa: E712
    elif status_filter == TaskStatus.COMPLETED:
        query = query.where(Task.completed == True)  # noqa: E712

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total_count = total_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Task, sort_by.value)
    if sort_by == TaskSortBy.DUE_DATE:
        # Null due_dates appear last when sorting
        if sort_order == SortOrder.ASC:
            query = query.order_by(sort_column.is_(None), sort_column.asc())
        else:
            query = query.order_by(sort_column.is_(None), sort_column.desc())
    else:
        if sort_order == SortOrder.ASC:
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    return TaskListResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total_count=total_count,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


async def get_task(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
) -> Task:
    """
    Get a single task with ownership check.

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task",
        )

    return task


async def update_task(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    task_data: TaskUpdate,
) -> Task:
    """
    Update a task with ownership check.

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    task = await get_task(session, task_id, user_id)

    # Update only provided fields
    if task_data.title is not None:
        task.title = task_data.title.strip()
    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None
    if task_data.due_date is not None:
        # Strip timezone info to match database timezone-naive datetimes
        task.due_date = task_data.due_date.replace(tzinfo=None) if task_data.due_date else None

    task.updated_at = datetime.utcnow()

    await session.flush()
    await session.refresh(task)
    return task


async def delete_task(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
) -> None:
    """
    Delete a task with ownership check.

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    task = await get_task(session, task_id, user_id)
    await session.delete(task)
    await session.flush()


async def toggle_complete(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
) -> Task:
    """
    Toggle task completion status.

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    task = await get_task(session, task_id, user_id)
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await session.flush()
    await session.refresh(task)
    return task
