"""
Reminder Event Handler

Processes reminder events from Kafka and logs notifications.
Uses IdempotencyService to prevent duplicate notifications.
"""
import structlog
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from app.services.idempotency import get_idempotency_service

logger = structlog.get_logger(__name__)


class ReminderEventData(BaseModel):
    """Reminder data from CloudEvent"""
    task_id: int
    user_id: UUID
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    remind_at: datetime
    reminder_type: str = "before_due"


class ReminderEvent(BaseModel):
    """CloudEvent wrapper for reminder"""
    specversion: str = "1.0"
    type: str
    source: str
    id: str  # Event ID for idempotency
    time: datetime
    data: ReminderEventData
    userid: UUID
    taskid: int


class ReminderHandler:
    """
    Handler for reminder events.

    Responsibilities:
    - Validate incoming reminder events
    - Check idempotency (prevent duplicate notifications)
    - Log notification (Phase 5 scope - actual delivery in future)
    - Mark event as processed
    """

    def __init__(self):
        """Initialize reminder handler."""
        self.idempotency = get_idempotency_service()

    async def handle_reminder(self, event_data: dict) -> dict:
        """
        Handle incoming reminder event.

        Args:
            event_data: Raw CloudEvent data from Dapr

        Returns:
            Processing result dict
        """
        try:
            # Parse event
            event = ReminderEvent.model_validate(event_data)

            logger.info(
                "reminder_event_received",
                event_id=event.id,
                task_id=event.taskid,
                user_id=str(event.userid),
                reminder_type=event.data.reminder_type
            )

            # Process with idempotency
            async def process():
                await self._send_notification(event)

            processed, result = await self.idempotency.process_with_idempotency(
                event_id=event.id,
                event_type=event.type,
                processor_func=process
            )

            return {
                "success": processed,
                "result": result,
                "event_id": event.id,
                "task_id": event.taskid
            }

        except Exception as e:
            logger.error(
                "reminder_handling_failed",
                error=str(e),
                event_data=str(event_data)[:500]
            )
            return {
                "success": False,
                "result": "error",
                "error": str(e)
            }

    async def _send_notification(self, event: ReminderEvent):
        """
        Send notification for reminder.

        Phase 5 Scope: Logs the notification
        Future: Email, Push, SMS delivery
        """
        notification_message = self._format_notification(event)

        # Log notification (Phase 5 scope)
        logger.info(
            "notification_sent",
            event_id=event.id,
            task_id=event.taskid,
            user_id=str(event.userid),
            title=event.data.title,
            reminder_type=event.data.reminder_type,
            message=notification_message
        )

        # Future: Actual notification delivery
        # await self._send_email(event.userid, notification_message)
        # await self._send_push(event.userid, notification_message)

    def _format_notification(self, event: ReminderEvent) -> str:
        """Format notification message."""
        if event.data.reminder_type == "before_due":
            if event.data.due_at:
                due_str = event.data.due_at.strftime("%Y-%m-%d %H:%M")
                return f"Reminder: '{event.data.title}' is due at {due_str}"
            else:
                return f"Reminder: '{event.data.title}'"
        elif event.data.reminder_type == "overdue":
            return f"Overdue: '{event.data.title}' was due and needs attention"
        else:
            return f"Task reminder: '{event.data.title}'"


# Singleton instance
_reminder_handler: Optional[ReminderHandler] = None


def get_reminder_handler() -> ReminderHandler:
    """Get singleton ReminderHandler instance."""
    global _reminder_handler
    if _reminder_handler is None:
        _reminder_handler = ReminderHandler()
    return _reminder_handler
