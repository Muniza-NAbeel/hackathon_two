"""
Notifications API Endpoints

Provides endpoints for managing user notifications.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth
from app.auth.jwt_handler import get_current_user_id
from app.db.database import get_session
from app.models.user import User
from app.models.task import Task

router = APIRouter(prefix="/api", tags=["notifications"])


class Notification(BaseModel):
    """Notification model"""
    id: str
    title: str
    message: str
    type: str  # 'info', 'success', 'error', 'reminder', 'recurring'
    timestamp: datetime
    read: bool = False
    task_id: Optional[int] = None


class NotificationsResponse(BaseModel):
    """Response for notifications endpoint"""
    notifications: List[Notification]
    total: int
    unread: int


@router.get("/notifications", response_model=NotificationsResponse)
async def get_notifications(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False
):
    """
    Get user notifications.

    Args:
        current_user: Authenticated user
        session: Database session
        limit: Number of notifications to return
        offset: Offset for pagination
        unread_only: If True, return only unread notifications

    Returns:
        NotificationsResponse: List of notifications
    """
    try:
        # Query for tasks for this user, focusing on recent activity
        # We'll consider completed tasks, tasks with reminders, and recurring tasks
        query = select(Task).where(Task.user_id == user_id)

        # Order by updated date, descending (most recent first)
        query = query.order_by(Task.updated_at.desc()).limit(limit).offset(offset)

        result = await session.execute(query)
        tasks = result.scalars().all()

        notifications = []

        # Process tasks to create appropriate notifications
        for task in tasks:
            # Create notifications based on task status and activity
            if task.completed:
                # Task completion notification
                notifications.append(Notification(
                    id=f"completion_{task.id}_{int(task.updated_at.timestamp())}",
                    title="Task Completed",
                    message=f'You completed the task "{task.title}"',
                    type="success",
                    timestamp=task.updated_at,
                    read=False,
                    task_id=task.id
                ))

            if task.remind_at:
                # Task reminder notification
                notifications.append(Notification(
                    id=f"reminder_{task.id}_{int(task.remind_at.timestamp())}",
                    title="Task Reminder",
                    message=f'Reminder: "{task.title}" is due soon',
                    type="reminder",
                    timestamp=task.remind_at,
                    read=False,
                    task_id=task.id
                ))

            if task.recurrence and task.recurrence != "none":
                # Recurring task notification
                notifications.append(Notification(
                    id=f"recurring_{task.id}_{int(task.updated_at.timestamp())}",
                    title="Recurring Task",
                    message=f'Your recurring task "{task.title}" is scheduled ({task.recurrence})',
                    type="recurring",
                    timestamp=task.updated_at,
                    read=False,
                    task_id=task.id
                ))

            if not task.completed and not task.remind_at and task.created_at:
                # New task notification
                notifications.append(Notification(
                    id=f"task_{task.id}_{int(task.created_at.timestamp())}",
                    title="New Task",
                    message=f'New task created: "{task.title}"',
                    type="info",
                    timestamp=task.created_at,
                    read=False,
                    task_id=task.id
                ))

        # Sort by timestamp, newest first
        notifications.sort(key=lambda x: x.timestamp, reverse=True)

        # Limit to requested number
        notifications = notifications[:limit]

        # Filter for unread if requested
        if unread_only:
            notifications = [n for n in notifications if not n.read]

        total = len(notifications)
        unread = len([n for n in notifications if not n.read])

        return NotificationsResponse(
            notifications=notifications,
            total=total,
            unread=unread
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Mark a notification as read.

    Args:
        notification_id: ID of the notification to mark as read
        current_user: Authenticated user
        session: Database session

    Returns:
        dict: Success message
    """
    # In a real implementation, we'd update the notification's read status in a notifications table
    # For now, we'll just return success
    return {"message": "Notification marked as read", "id": notification_id}


@router.delete("/notifications")
async def clear_notifications(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Clear all notifications for the user.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        dict: Success message
    """
    # In a real implementation, we'd clear the user's notifications from a notifications table
    # For now, we'll just return success
    return {"message": "All notifications cleared"}