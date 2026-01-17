"""Tasks router with CRUD endpoints and ownership enforcement."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.middleware.auth import get_current_user, verify_user_ownership
from app.models.user import User
from app.schemas.auth import ErrorResponse
from app.schemas.task import (
    SortOrder,
    TaskCreate,
    TaskListResponse,
    TaskRead,
    TaskSortBy,
    TaskStatus,
    TaskUpdate,
)
from app.services import task as task_service

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def list_tasks(
    user_id: UUID,
    status: TaskStatus = Query(TaskStatus.ALL, description="Filter by completion status"),
    sort_by: TaskSortBy = Query(TaskSortBy.CREATED_AT, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskListResponse:
    """List tasks for the authenticated user with filtering and pagination."""
    verify_user_ownership(user_id, current_user)

    return await task_service.get_tasks(
        session=session,
        user_id=user_id,
        status_filter=status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        422: {"description": "Validation error"},
    },
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Create a new task for the authenticated user."""
    verify_user_ownership(user_id, current_user)

    task = await task_service.create_task(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )
    return TaskRead.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def get_task(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Get a specific task by ID."""
    verify_user_ownership(user_id, current_user)

    task = await task_service.get_task(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )
    return TaskRead.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
async def update_task(
    user_id: UUID,
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Update a task by ID."""
    verify_user_ownership(user_id, current_user)

    task = await task_service.update_task(
        session=session,
        task_id=task_id,
        user_id=user_id,
        task_data=task_data,
    )
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def delete_task(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a task by ID."""
    verify_user_ownership(user_id, current_user)

    await task_service.delete_task(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def toggle_task_complete(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Toggle task completion status."""
    verify_user_ownership(user_id, current_user)

    task = await task_service.toggle_complete(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )
    return TaskRead.model_validate(task)
