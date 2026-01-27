"""
Reminder Checker Service

Checks for tasks with pending reminders and publishes reminder events.
Called by Dapr Cron binding every 5 minutes.
"""
import structlog
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.events.publisher import get_event_publisher

logger = structlog.get_logger(__name__)


class ReminderChecker:
    """
    Service for checking and processing task reminders.

    Flow:
    1. Query tasks where remind_at <= now AND reminder_sent = false
    2. For each task, publish reminder event
    3. Mark reminder_sent = true to prevent duplicates
    """

    def __init__(self, batch_size: int = 100):
        """
        Initialize reminder checker.

        Args:
            batch_size: Maximum reminders to process per check
        """
        self.batch_size = batch_size
        self.publisher = get_event_publisher()

    async def check_and_send_reminders(
        self,
        session: AsyncSession
    ) -> dict:
        """
        Check for due reminders and publish events.

        Args:
            session: Database session

        Returns:
            Summary of processed reminders
        """
        now = datetime.utcnow()
        processed = 0
        errors = 0

        try:
            # Query tasks with pending reminders
            query = select(Task).where(
                and_(
                    Task.remind_at <= now,
                    Task.reminder_sent == False,
                    Task.status != "completed"  # Don't remind for completed tasks
                )
            ).limit(self.batch_size)

            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(
                "reminder_check_started",
                pending_count=len(tasks),
                check_time=str(now)
            )

            for task in tasks:
                try:
                    # Determine reminder type
                    reminder_type = "before_due"
                    if task.due_date and task.due_date < now:
                        reminder_type = "overdue"

                    # Publish reminder event
                    success = await self.publisher.publish_reminder_event(
                        task_id=task.id,
                        user_id=task.user_id,
                        title=task.title,
                        description=task.description,
                        due_at=task.due_date,
                        remind_at=task.remind_at,
                        reminder_type=reminder_type
                    )

                    if success:
                        # Mark reminder as sent
                        task.reminder_sent = True
                        task.updated_at = now
                        processed += 1

                        logger.info(
                            "reminder_sent",
                            task_id=task.id,
                            user_id=str(task.user_id),
                            reminder_type=reminder_type
                        )
                    else:
                        errors += 1
                        logger.error(
                            "reminder_publish_failed",
                            task_id=task.id
                        )

                except Exception as e:
                    errors += 1
                    logger.error(
                        "reminder_processing_error",
                        task_id=task.id,
                        error=str(e)
                    )

            # Commit all updates
            await session.commit()

            logger.info(
                "reminder_check_completed",
                processed=processed,
                errors=errors
            )

            return {
                "processed": processed,
                "errors": errors,
                "next_check": datetime.utcnow()
            }

        except Exception as e:
            logger.error("reminder_check_failed", error=str(e))
            return {
                "processed": processed,
                "errors": errors + 1,
                "error": str(e)
            }


# Singleton instance
_reminder_checker: Optional[ReminderChecker] = None


def get_reminder_checker() -> ReminderChecker:
    """Get singleton ReminderChecker instance."""
    global _reminder_checker
    if _reminder_checker is None:
        _reminder_checker = ReminderChecker()
    return _reminder_checker
