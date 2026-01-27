"""
MCP Tools Implementation (Integrated in Backend)

All 5 MCP tools as per PDF specification:
- add_task: Create a new task
- list_tasks: List tasks with optional filters
- complete_task: Mark a task as complete
- delete_task: Remove a task
- update_task: Update task details

These tools are called directly by the AI agent without HTTP.
Uses async SQLAlchemy sessions for database operations.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select, desc

from app.db.database import async_session_maker
from app.models.task import Task

logger = logging.getLogger(__name__)


# ============================================================================
# Response Model
# ============================================================================

class MCPResponse(BaseModel):
    """Standard MCP tool response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# ============================================================================
# MCP Tool: add_task
# ============================================================================

async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
) -> MCPResponse:
    """
    MCP Tool: add_task

    Create a new task for the user.

    Args:
        user_id: UUID of the user (as string)
        title: Task title (required)
        description: Task description (optional)
        priority: Priority level - low, medium, high, urgent (optional)
        tags: List of tags (optional)
        due_date: Due date in ISO format (optional)

    Returns:
        MCPResponse with task_id, title, and status
    """
    try:
        logger.info(f"MCP add_task: user={user_id}, title={title}")

        user_uuid = UUID(user_id)

        # Parse due_date if provided
        due_date_obj = None
        if due_date:
            try:
                from dateutil import parser
                due_date_obj = parser.parse(due_date)
            except Exception as e:
                logger.warning(f"Failed to parse due_date '{due_date}': {e}")

        async with async_session_maker() as session:
            task = Task(
                user_id=user_uuid,
                title=title,
                description=description,
                completed=False,
                status="pending",
                priority=priority or "medium",
                tags=tags,
                due_date=due_date_obj,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"MCP add_task: Created task #{task.id}")

            return MCPResponse(
                success=True,
                message=f"Task created successfully! Task ID: {task.id}",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": str(task.due_date) if task.due_date else None,
                }
            )

    except Exception as e:
        logger.error(f"MCP add_task error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error creating task: {str(e)}",
            data=None
        )


# ============================================================================
# MCP Tool: list_tasks
# ============================================================================

async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
) -> MCPResponse:
    """
    MCP Tool: list_tasks

    List all tasks for a user with optional status filter.

    Args:
        user_id: UUID of the user (as string)
        status: Filter by status - "completed", "pending", or None for all

    Returns:
        MCPResponse with list of tasks and count
    """
    try:
        logger.info(f"MCP list_tasks: user={user_id}, status={status}")

        user_uuid = UUID(user_id)

        async with async_session_maker() as session:
            statement = select(Task).where(Task.user_id == user_uuid)

            # Apply status filter
            if status == "completed":
                statement = statement.where(Task.completed == True)
            elif status == "pending":
                statement = statement.where(Task.completed == False)

            statement = statement.order_by(desc(Task.created_at))
            result = await session.execute(statement)
            tasks = result.scalars().all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": str(task.due_date) if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                })

            logger.info(f"MCP list_tasks: Found {len(tasks)} task(s)")

            return MCPResponse(
                success=True,
                message=f"Found {len(tasks)} task(s)",
                data={"tasks": task_list, "count": len(tasks)}
            )

    except Exception as e:
        logger.error(f"MCP list_tasks error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error listing tasks: {str(e)}",
            data={"tasks": [], "count": 0}
        )


# ============================================================================
# MCP Tool: complete_task
# ============================================================================

async def complete_task(
    user_id: str,
    task_id: int,
) -> MCPResponse:
    """
    MCP Tool: complete_task

    Mark a task as complete.

    Args:
        user_id: UUID of the user (as string)
        task_id: ID of the task to complete

    Returns:
        MCPResponse with task_id, title, and status
    """
    try:
        logger.info(f"MCP complete_task: user={user_id}, task_id={task_id}")

        user_uuid = UUID(user_id)

        async with async_session_maker() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_uuid
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"MCP complete_task: Task {task_id} not found")
                return MCPResponse(
                    success=False,
                    message=f"Task {task_id} not found",
                    data=None
                )

            task.completed = True
            task.status = "completed"
            task.updated_at = datetime.utcnow()
            await session.commit()

            logger.info(f"MCP complete_task: Completed task #{task_id}")

            return MCPResponse(
                success=True,
                message=f"Task '{task.title}' marked as complete!",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                }
            )

    except Exception as e:
        logger.error(f"MCP complete_task error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error completing task: {str(e)}",
            data=None
        )


# ============================================================================
# MCP Tool: delete_task
# ============================================================================

async def delete_task(
    user_id: str,
    task_id: int,
) -> MCPResponse:
    """
    MCP Tool: delete_task

    Delete a task.

    Args:
        user_id: UUID of the user (as string)
        task_id: ID of the task to delete

    Returns:
        MCPResponse with task_id and status
    """
    try:
        logger.info(f"MCP delete_task: user={user_id}, task_id={task_id}")

        user_uuid = UUID(user_id)

        async with async_session_maker() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_uuid
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"MCP delete_task: Task {task_id} not found")
                return MCPResponse(
                    success=False,
                    message=f"Task {task_id} not found",
                    data=None
                )

            title = task.title
            await session.delete(task)
            await session.commit()

            logger.info(f"MCP delete_task: Deleted task #{task_id}")

            return MCPResponse(
                success=True,
                message=f"Task '{title}' deleted successfully!",
                data={"task_id": task_id, "title": title}
            )

    except Exception as e:
        logger.error(f"MCP delete_task error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error deleting task: {str(e)}",
            data=None
        )


# ============================================================================
# MCP Tool: update_task
# ============================================================================

async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> MCPResponse:
    """
    MCP Tool: update_task

    Update task title, description, status, or priority.

    Args:
        user_id: UUID of the user (as string)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status - "completed" or "pending" (optional)
        priority: New priority - low, medium, high, urgent (optional)

    Returns:
        MCPResponse with updated task details
    """
    try:
        logger.info(f"MCP update_task: user={user_id}, task_id={task_id}")

        user_uuid = UUID(user_id)

        async with async_session_maker() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_uuid
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"MCP update_task: Task {task_id} not found")
                return MCPResponse(
                    success=False,
                    message=f"Task {task_id} not found",
                    data=None
                )

            # Update fields
            if title:
                task.title = title
            if description is not None:
                task.description = description
            if status:
                task.completed = (status == "completed")
                task.status = status
            if priority:
                task.priority = priority

            task.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(task)

            logger.info(f"MCP update_task: Updated task #{task_id}")

            return MCPResponse(
                success=True,
                message=f"Task '{task.title}' updated successfully!",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "status": task.status,
                    "priority": task.priority,
                }
            )

    except Exception as e:
        logger.error(f"MCP update_task error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error updating task: {str(e)}",
            data=None
        )


# ============================================================================
# MCP Tool: set_reminder (Phase 5)
# ============================================================================

async def set_reminder(
    user_id: str,
    task_id: int,
    remind_at: str,
) -> MCPResponse:
    """
    MCP Tool: set_reminder (Phase 5)

    Set a reminder for a task. The reminder will trigger a notification
    at the specified time via the event-driven notification service.

    Args:
        user_id: UUID of the user (as string)
        task_id: ID of the task to set reminder for
        remind_at: Reminder time in ISO format (e.g., "2026-01-20T09:00:00")

    Returns:
        MCPResponse with reminder details
    """
    try:
        logger.info(f"MCP set_reminder: user={user_id}, task_id={task_id}, remind_at={remind_at}")

        user_uuid = UUID(user_id)

        # Parse remind_at
        remind_at_obj = None
        try:
            from dateutil import parser
            remind_at_obj = parser.parse(remind_at)
            # Strip timezone for database compatibility
            if remind_at_obj.tzinfo:
                remind_at_obj = remind_at_obj.replace(tzinfo=None)
        except Exception as e:
            return MCPResponse(
                success=False,
                message=f"Invalid remind_at format: {remind_at}. Use ISO format like '2026-01-20T09:00:00'",
                data=None
            )

        async with async_session_maker() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_uuid
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"MCP set_reminder: Task {task_id} not found")
                return MCPResponse(
                    success=False,
                    message=f"Task {task_id} not found",
                    data=None
                )

            # Set reminder
            task.remind_at = remind_at_obj
            task.reminder_sent = False  # Reset in case it was already sent
            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            logger.info(f"MCP set_reminder: Set reminder for task #{task_id} at {remind_at_obj}")

            return MCPResponse(
                success=True,
                message=f"Reminder set for '{task.title}' at {remind_at_obj.strftime('%Y-%m-%d %H:%M')}",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "remind_at": remind_at_obj.isoformat(),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                }
            )

    except Exception as e:
        logger.error(f"MCP set_reminder error: {e}")
        return MCPResponse(
            success=False,
            message=f"Error setting reminder: {str(e)}",
            data=None
        )
