"""
Event Publisher Service

Publishes task lifecycle and reminder events to Kafka via Dapr Pub/Sub.
Uses CloudEvents v1.0 format for all events.
"""
import os
import structlog
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .dapr_client import DaprClient, get_dapr_client
from .schemas import (
    TaskEvent,
    TaskEventData,
    TaskEventType,
    ReminderEvent,
    ReminderEventData,
)

logger = structlog.get_logger(__name__)


class EventPublisher:
    """
    Event publisher for task lifecycle events.

    Publishes events to Kafka topics via Dapr Pub/Sub:
    - task-events: Task CRUD events (created, updated, completed, deleted)
    - reminders: Reminder notification events

    Environment Variables:
    - DAPR_PUBSUB_NAME: Pub/Sub component name (default: "kafka-pubsub")
    - TASK_EVENTS_TOPIC: Topic for task events (default: "task-events")
    - REMINDERS_TOPIC: Topic for reminders (default: "reminders")
    """

    def __init__(
        self,
        dapr_client: Optional[DaprClient] = None,
        pubsub_name: Optional[str] = None,
        task_events_topic: Optional[str] = None,
        reminders_topic: Optional[str] = None
    ):
        """
        Initialize event publisher.

        Args:
            dapr_client: Dapr client instance (uses singleton if not provided)
            pubsub_name: Pub/Sub component name
            task_events_topic: Topic for task events
            reminders_topic: Topic for reminder events
        """
        self.dapr_client = dapr_client or get_dapr_client()
        self.pubsub_name = pubsub_name or os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
        self.task_events_topic = task_events_topic or os.getenv("TASK_EVENTS_TOPIC", "task-events")
        self.reminders_topic = reminders_topic or os.getenv("REMINDERS_TOPIC", "reminders")

    async def publish_task_event(
        self,
        event_type: TaskEventType,
        task_id: int,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        status: str = "pending",
        completed: bool = False,
        priority: str = "medium",
        tags: Optional[list] = None,
        recurrence: str = "none",
        due_date: Optional[datetime] = None,
        remind_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        """
        Publish task lifecycle event to Kafka.

        Args:
            event_type: Type of task event (created, updated, completed, deleted)
            task_id: Task ID
            user_id: User ID who owns the task
            title: Task title
            description: Task description
            status: Task status
            completed: Whether task is completed
            priority: Task priority
            tags: Task tags
            recurrence: Recurrence pattern
            due_date: Task due date
            remind_at: Reminder time
            created_at: Task creation time
            updated_at: Task update time

        Returns:
            True if published successfully
        """
        now = datetime.utcnow()

        # Build event data
        event_data = TaskEventData(
            id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            completed=completed,
            priority=priority,
            tags=tags,
            recurrence=recurrence,
            due_date=due_date,
            remind_at=remind_at,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )

        # Build CloudEvent
        event = TaskEvent(
            id=uuid4(),
            type=event_type.value,
            time=now,
            data=event_data,
            userid=user_id,
            taskid=task_id,
        )

        # Publish to Kafka
        success = await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic=self.task_events_topic,
            data=event.model_dump(mode="json"),
            metadata={"partitionKey": str(user_id)}  # Partition by user for ordering
        )

        if success:
            logger.info(
                "task_event_published",
                event_type=event_type.value,
                event_id=str(event.id),
                task_id=task_id,
                user_id=str(user_id),
                topic=self.task_events_topic
            )
        else:
            logger.error(
                "task_event_publish_failed",
                event_type=event_type.value,
                task_id=task_id,
                user_id=str(user_id)
            )

        return success

    async def publish_task_created(self, task) -> bool:
        """Publish task created event."""
        return await self.publish_task_event(
            event_type=TaskEventType.CREATED,
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            completed=task.completed,
            priority=task.priority,
            tags=task.tags,
            recurrence=task.recurrence,
            due_date=task.due_date,
            remind_at=getattr(task, 'remind_at', None),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    async def publish_task_updated(self, task) -> bool:
        """Publish task updated event."""
        return await self.publish_task_event(
            event_type=TaskEventType.UPDATED,
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            completed=task.completed,
            priority=task.priority,
            tags=task.tags,
            recurrence=task.recurrence,
            due_date=task.due_date,
            remind_at=getattr(task, 'remind_at', None),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    async def publish_task_completed(self, task) -> bool:
        """Publish task completed event."""
        return await self.publish_task_event(
            event_type=TaskEventType.COMPLETED,
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            completed=True,
            priority=task.priority,
            tags=task.tags,
            recurrence=task.recurrence,
            due_date=task.due_date,
            remind_at=getattr(task, 'remind_at', None),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    async def publish_task_deleted(
        self,
        task_id: int,
        user_id: UUID,
        title: str
    ) -> bool:
        """Publish task deleted event."""
        return await self.publish_task_event(
            event_type=TaskEventType.DELETED,
            task_id=task_id,
            user_id=user_id,
            title=title,
            status="deleted",
            completed=False,
        )

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        due_at: Optional[datetime] = None,
        remind_at: Optional[datetime] = None,
        reminder_type: str = "before_due"
    ) -> bool:
        """
        Publish reminder event to Kafka.

        Args:
            task_id: Task ID
            user_id: User ID
            title: Task title
            description: Task description
            due_at: Task due date
            remind_at: Scheduled reminder time
            reminder_type: Type of reminder (before_due, overdue)

        Returns:
            True if published successfully
        """
        now = datetime.utcnow()

        # Build event data
        event_data = ReminderEventData(
            task_id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            due_at=due_at,
            remind_at=remind_at or now,
            reminder_type=reminder_type,
        )

        # Build CloudEvent
        event = ReminderEvent(
            id=uuid4(),
            time=now,
            data=event_data,
            userid=user_id,
            taskid=task_id,
        )

        # Publish to Kafka
        success = await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic=self.reminders_topic,
            data=event.model_dump(mode="json"),
            metadata={"partitionKey": str(user_id)}
        )

        if success:
            logger.info(
                "reminder_event_published",
                event_id=str(event.id),
                task_id=task_id,
                user_id=str(user_id),
                reminder_type=reminder_type,
                topic=self.reminders_topic
            )
        else:
            logger.error(
                "reminder_event_publish_failed",
                task_id=task_id,
                user_id=str(user_id)
            )

        return success


# Singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get singleton EventPublisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
