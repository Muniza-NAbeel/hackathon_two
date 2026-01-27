"""
Task Completed Event Handler

Processes task.completed events and creates next recurring task instance.
Uses IdempotencyService to prevent duplicate task creation.
"""
import structlog
import base64
import json
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from uuid import UUID

from app.services.recurrence import get_recurrence_calculator
from app.services.task_creator import get_task_creator
from app.services.idempotency import get_idempotency_service

logger = structlog.get_logger(__name__)


class TaskEventData(BaseModel):
    """Task data from CloudEvent"""
    id: int
    user_id: UUID
    title: str
    description: Optional[str] = None
    status: str
    completed: bool
    priority: str
    tags: Optional[list[str]] = None
    recurrence: str
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskEvent(BaseModel):
    """CloudEvent wrapper for task events"""
    specversion: str = "1.0"
    type: str
    source: str = "todo-backend"
    id: str  # Event ID for idempotency
    time: datetime
    data: TaskEventData
    userid: UUID
    taskid: int


def unwrap_dapr_envelope(event_data: dict) -> dict:
    """
    Unwrap Dapr CloudEvents envelope to get the actual event data.

    Dapr can send events in different formats:
    1. data_base64 (raw payload mode) - base64 encoded CloudEvent
    2. data (standard mode) - nested data object
    3. Direct CloudEvent (no wrapper)

    Args:
        event_data: Raw event from Dapr

    Returns:
        Unwrapped CloudEvent data
    """
    logger.debug("unwrapping_dapr_event", keys=list(event_data.keys()))

    # Case 1: data_base64 present (rawPayload mode)
    if "data_base64" in event_data:
        try:
            decoded = base64.b64decode(event_data["data_base64"])
            inner_event = json.loads(decoded)
            logger.debug("decoded_base64_event", inner_keys=list(inner_event.keys()))

            # Check if inner event has 'data' containing the CloudEvent
            if "data" in inner_event and isinstance(inner_event["data"], dict):
                cloud_event = inner_event.get("data", {})

                # If cloud_event has nested 'data', that's our TaskEventData
                if "data" in cloud_event and isinstance(cloud_event["data"], dict):
                    # This is our actual CloudEvent structure
                    return cloud_event

            # Maybe the decoded data IS the CloudEvent directly
            return inner_event

        except Exception as e:
            logger.error("base64_decode_failed", error=str(e))
            raise

    # Case 2: Standard Dapr envelope with nested 'data'
    if "data" in event_data and isinstance(event_data["data"], dict):
        inner_data = event_data["data"]

        # Check if this 'data' contains another 'data' (double nesting)
        if "data" in inner_data and isinstance(inner_data["data"], dict):
            # inner_data is the CloudEvent, inner_data['data'] is TaskEventData
            return inner_data

        # inner_data might be the TaskEventData directly
        # In this case, use the outer envelope as CloudEvent
        return event_data

    # Case 3: Direct CloudEvent (no wrapper) - has required fields
    required_fields = {"type", "id", "data"}
    if required_fields.issubset(event_data.keys()):
        return event_data

    logger.warning("unknown_event_format", event_keys=list(event_data.keys()))
    return event_data


class TaskCompletedHandler:
    """
    Handler for task.completed events.

    Responsibilities:
    - Filter for task.completed events only
    - Check if task is recurring
    - Calculate next due date
    - Create new task instance via backend
    - Ensure idempotency
    """

    TASK_COMPLETED_TYPE = "com.todo.task.completed"

    def __init__(self):
        """Initialize handler with required services."""
        self.recurrence = get_recurrence_calculator()
        self.task_creator = get_task_creator()
        self.idempotency = get_idempotency_service()

    async def handle_task_event(self, event_data: dict) -> dict:
        """
        Handle incoming task event.

        Only processes task.completed events for recurring tasks.

        Args:
            event_data: Raw CloudEvent data from Dapr

        Returns:
            Processing result dict
        """
        try:
            # Unwrap Dapr envelope to get actual CloudEvent
            unwrapped_data = unwrap_dapr_envelope(event_data)
            logger.debug("event_unwrapped", unwrapped_keys=list(unwrapped_data.keys()))

            # Parse event
            event = TaskEvent.model_validate(unwrapped_data)

            # Only process task.completed events
            if event.type != self.TASK_COMPLETED_TYPE:
                logger.debug(
                    "ignoring_non_completed_event",
                    event_type=event.type,
                    event_id=event.id
                )
                return {
                    "success": True,
                    "result": "ignored",
                    "reason": "not_completed_event"
                }

            logger.info(
                "task_completed_event_received",
                event_id=event.id,
                task_id=event.taskid,
                user_id=str(event.userid),
                recurrence=event.data.recurrence
            )

            # Check if recurring
            if not self.recurrence.is_recurring(event.data.recurrence):
                logger.info(
                    "task_not_recurring",
                    task_id=event.taskid,
                    recurrence=event.data.recurrence
                )
                return {
                    "success": True,
                    "result": "skipped",
                    "reason": "not_recurring"
                }

            # Check idempotency
            if await self.idempotency.is_processed(event.id):
                logger.info(
                    "duplicate_event_skipped",
                    event_id=event.id,
                    task_id=event.taskid
                )
                return {
                    "success": True,
                    "result": "skipped",
                    "reason": "duplicate"
                }

            # Process the recurring task
            result = await self._create_next_instance(event)

            # Mark as processed
            if result.get("success"):
                await self.idempotency.mark_processed(
                    event_id=event.id,
                    event_type=event.type,
                    result="success",
                    new_task_id=result.get("new_task_id")
                )

            return result

        except Exception as e:
            logger.error(
                "task_completed_handling_failed",
                error=str(e),
                event_data=str(event_data)[:500]
            )
            return {
                "success": False,
                "result": "error",
                "error": str(e)
            }

    async def _create_next_instance(self, event: TaskEvent) -> dict:
        """
        Create the next instance of a recurring task.

        Args:
            event: Parsed task.completed event

        Returns:
            Result dict with new task info
        """
        task_data = event.data

        # Calculate next due date
        next_due_date = self.recurrence.calculate_next_due_date(
            current_due_date=task_data.due_date,
            recurrence=task_data.recurrence,
            completed_at=task_data.updated_at
        )

        # Calculate next reminder time
        next_remind_at = self.recurrence.calculate_next_remind_at(
            current_remind_at=task_data.remind_at,
            current_due_date=task_data.due_date,
            next_due_date=next_due_date,
            recurrence=task_data.recurrence
        )

        logger.info(
            "creating_next_recurring_task",
            original_task_id=task_data.id,
            recurrence=task_data.recurrence,
            next_due_date=str(next_due_date),
            next_remind_at=str(next_remind_at)
        )

        # Create new task via backend
        original_task_dict = {
            "id": task_data.id,
            "user_id": str(task_data.user_id),
            "title": task_data.title,
            "description": task_data.description,
            "priority": task_data.priority,
            "tags": task_data.tags,
            "recurrence": task_data.recurrence,
        }

        new_task = await self.task_creator.create_recurring_task_instance(
            original_task=original_task_dict,
            next_due_date=next_due_date,
            next_remind_at=next_remind_at
        )

        if new_task:
            logger.info(
                "recurring_task_created",
                original_task_id=task_data.id,
                new_task_id=new_task.get("id"),
                user_id=str(task_data.user_id)
            )
            return {
                "success": True,
                "result": "created",
                "original_task_id": task_data.id,
                "new_task_id": new_task.get("id"),
                "next_due_date": str(next_due_date)
            }
        else:
            logger.error(
                "recurring_task_creation_failed",
                original_task_id=task_data.id,
                user_id=str(task_data.user_id)
            )
            return {
                "success": False,
                "result": "error",
                "error": "Failed to create recurring task"
            }


# Singleton instance
_handler: Optional[TaskCompletedHandler] = None


def get_task_completed_handler() -> TaskCompletedHandler:
    """Get singleton TaskCompletedHandler instance."""
    global _handler
    if _handler is None:
        _handler = TaskCompletedHandler()
    return _handler
