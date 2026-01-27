"""
Internal API Endpoints

Service-to-service endpoints not exposed publicly.
Used by Dapr Service Invocation from other microservices.
Includes Dapr Cron binding endpoint for reminder checks.
"""
import structlog
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.models.task import Task
from app.services.reminder_checker import get_reminder_checker

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/internal", tags=["internal"])


class InternalTaskCreate(BaseModel):
    """Request to create task from internal service"""
    user_id: str  # UUID as string
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    tags: Optional[list[str]] = None
    recurrence: str = "none"
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    source_task_id: Optional[int] = None


class InternalTaskResponse(BaseModel):
    """Response from internal task creation"""
    id: int
    user_id: str
    title: str
    status: str
    recurrence: str
    due_date: Optional[datetime]
    created_at: datetime


@router.post("/tasks", response_model=InternalTaskResponse)
async def create_internal_task(
    task_data: InternalTaskCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a task from internal service (e.g., recurring-task-service).

    This endpoint is called via Dapr Service Invocation.
    No JWT authentication required - internal network only.
    """
    try:
        user_id = UUID(task_data.user_id)

        # Strip timezone info if present
        due_date = task_data.due_date
        if due_date and due_date.tzinfo:
            due_date = due_date.replace(tzinfo=None)

        remind_at = task_data.remind_at
        if remind_at and remind_at.tzinfo:
            remind_at = remind_at.replace(tzinfo=None)

        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status="pending",
            tags=task_data.tags,
            recurrence=task_data.recurrence,
            due_date=due_date,
            remind_at=remind_at,
        )

        session.add(task)
        await session.flush()
        await session.refresh(task)
        await session.commit()

        logger.info(
            "internal_task_created",
            task_id=task.id,
            user_id=str(user_id),
            title=task.title,
            source_task_id=task_data.source_task_id,
            recurrence=task.recurrence
        )

        return InternalTaskResponse(
            id=task.id,
            user_id=str(task.user_id),
            title=task.title,
            status=task.status,
            recurrence=task.recurrence,
            due_date=task.due_date,
            created_at=task.created_at
        )

    except Exception as e:
        logger.error("internal_task_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


class ReminderCheckResponse(BaseModel):
    """Response from reminder check endpoint"""
    processed: int
    errors: int
    next_check: Optional[datetime] = None
    error: Optional[str] = None


@router.post("/reminder-cron", response_model=ReminderCheckResponse)
async def handle_reminder_cron(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Handle Dapr Cron binding trigger for reminder checks.

    Called every 5 minutes by Dapr Cron binding.
    Checks for due reminders and publishes events.
    """
    logger.info("reminder_cron_triggered")

    try:
        checker = get_reminder_checker()
        result = await checker.check_and_send_reminders(session)

        return ReminderCheckResponse(
            processed=result.get("processed", 0),
            errors=result.get("errors", 0),
            next_check=result.get("next_check"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error("reminder_cron_failed", error=str(e))
        return ReminderCheckResponse(
            processed=0,
            errors=1,
            error=str(e)
        )
