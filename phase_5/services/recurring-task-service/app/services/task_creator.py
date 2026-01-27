"""
Task Creator Service using Dapr Service Invocation

Creates new tasks in the backend service via Dapr Service Invocation.
This provides automatic service discovery, load balancing, and mTLS.
"""
import os
import httpx
import structlog
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "chat-backend")


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
    source_task_id: Optional[int] = None  # Original recurring task


class InternalTaskResponse(BaseModel):
    """Response from internal task creation"""
    id: int
    user_id: str
    title: str
    status: str
    created_at: datetime


class TaskCreator:
    """
    Service for creating tasks via Dapr Service Invocation.

    Uses Dapr sidecar to invoke the backend's internal task creation endpoint.
    Benefits:
    - Automatic service discovery
    - Load balancing across backend replicas
    - mTLS encryption
    - Automatic retries
    """

    def __init__(
        self,
        backend_app_id: Optional[str] = None,
        dapr_port: Optional[int] = None
    ):
        """
        Initialize task creator.

        Args:
            backend_app_id: Dapr app ID for backend service
            dapr_port: Dapr sidecar HTTP port
        """
        self.backend_app_id = backend_app_id or BACKEND_APP_ID
        self.dapr_port = dapr_port or DAPR_HTTP_PORT
        self.dapr_url = f"http://localhost:{self.dapr_port}"

    async def create_task(
        self,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[list[str]] = None,
        recurrence: str = "none",
        due_date: Optional[datetime] = None,
        remind_at: Optional[datetime] = None,
        source_task_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Create a new task via backend service.

        Args:
            user_id: Owner's user ID
            title: Task title
            description: Task description
            priority: Task priority
            tags: Task tags
            recurrence: Recurrence pattern for the new task
            due_date: Due date for the new task
            remind_at: Reminder time for the new task
            source_task_id: ID of the original recurring task

        Returns:
            Created task data or None on failure
        """
        url = f"{self.dapr_url}/v1.0/invoke/{self.backend_app_id}/method/api/internal/tasks"

        task_data = {
            "user_id": str(user_id),
            "title": title,
            "description": description,
            "priority": priority,
            "tags": tags,
            "recurrence": recurrence,
            "source_task_id": source_task_id
        }

        # Add dates if provided (as ISO strings)
        if due_date:
            task_data["due_date"] = due_date.isoformat()
        if remind_at:
            task_data["remind_at"] = remind_at.isoformat()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=task_data,
                    timeout=10.0,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201):
                    result = response.json()
                    logger.info(
                        "task_created_via_dapr",
                        new_task_id=result.get("id"),
                        user_id=str(user_id),
                        source_task_id=source_task_id,
                        title=title
                    )
                    return result
                else:
                    logger.error(
                        "task_creation_failed",
                        status_code=response.status_code,
                        response=response.text[:500],
                        user_id=str(user_id)
                    )
                    return None

        except httpx.RequestError as e:
            logger.error(
                "dapr_invocation_error",
                error=str(e),
                backend_app_id=self.backend_app_id,
                user_id=str(user_id)
            )
            return None

    async def create_recurring_task_instance(
        self,
        original_task: dict,
        next_due_date: Optional[datetime],
        next_remind_at: Optional[datetime]
    ) -> Optional[dict]:
        """
        Create next instance of a recurring task.

        Args:
            original_task: Original completed task data
            next_due_date: Calculated next due date
            next_remind_at: Calculated next reminder time

        Returns:
            Created task data or None on failure
        """
        return await self.create_task(
            user_id=UUID(original_task["user_id"]) if isinstance(original_task["user_id"], str) else original_task["user_id"],
            title=original_task["title"],
            description=original_task.get("description"),
            priority=original_task.get("priority", "medium"),
            tags=original_task.get("tags"),
            recurrence=original_task.get("recurrence", "none"),
            due_date=next_due_date,
            remind_at=next_remind_at,
            source_task_id=original_task.get("id")
        )


# Singleton instance
_task_creator: Optional[TaskCreator] = None


def get_task_creator() -> TaskCreator:
    """Get singleton TaskCreator instance."""
    global _task_creator
    if _task_creator is None:
        _task_creator = TaskCreator()
    return _task_creator
