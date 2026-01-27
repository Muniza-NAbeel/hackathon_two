"""
Recurrence Calculator Service

Calculates next occurrence dates for recurring tasks.
Supports daily, weekly, and monthly recurrence patterns.
"""
import structlog
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional

logger = structlog.get_logger(__name__)


class RecurrenceCalculator:
    """
    Calculator for recurring task due dates.

    Supported patterns:
    - daily: Next day
    - weekly: Next week (same day of week)
    - monthly: Next month (same day of month)
    """

    VALID_PATTERNS = {"none", "daily", "weekly", "monthly"}

    def calculate_next_due_date(
        self,
        current_due_date: Optional[datetime],
        recurrence: str,
        completed_at: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate the next due date based on recurrence pattern.

        Args:
            current_due_date: Current task due date
            recurrence: Recurrence pattern (daily, weekly, monthly)
            completed_at: When the task was completed (used if no due_date)

        Returns:
            Next due date, or None if not recurring
        """
        if recurrence not in self.VALID_PATTERNS or recurrence == "none":
            return None

        # Use current due date or completed time as base
        base_date = current_due_date or completed_at or datetime.utcnow()

        if recurrence == "daily":
            next_date = base_date + timedelta(days=1)
        elif recurrence == "weekly":
            next_date = base_date + timedelta(weeks=1)
        elif recurrence == "monthly":
            next_date = base_date + relativedelta(months=1)
        else:
            return None

        logger.debug(
            "next_due_date_calculated",
            recurrence=recurrence,
            current_due=str(current_due_date),
            next_due=str(next_date)
        )

        return next_date

    def calculate_next_remind_at(
        self,
        current_remind_at: Optional[datetime],
        current_due_date: Optional[datetime],
        next_due_date: Optional[datetime],
        recurrence: str
    ) -> Optional[datetime]:
        """
        Calculate the next reminder time based on the offset from due date.

        If original task had a reminder set before due date, maintain
        the same offset for the next occurrence.

        Args:
            current_remind_at: Current reminder time
            current_due_date: Current due date
            next_due_date: Calculated next due date
            recurrence: Recurrence pattern

        Returns:
            Next reminder time, or None if no reminder
        """
        if not current_remind_at or not next_due_date:
            return None

        if current_due_date:
            # Calculate offset between reminder and due date
            offset = current_due_date - current_remind_at
            next_remind_at = next_due_date - offset
        else:
            # If no due date, use same recurrence interval for reminder
            if recurrence == "daily":
                next_remind_at = current_remind_at + timedelta(days=1)
            elif recurrence == "weekly":
                next_remind_at = current_remind_at + timedelta(weeks=1)
            elif recurrence == "monthly":
                next_remind_at = current_remind_at + relativedelta(months=1)
            else:
                return None

        logger.debug(
            "next_remind_at_calculated",
            current_remind=str(current_remind_at),
            next_remind=str(next_remind_at)
        )

        return next_remind_at

    def is_recurring(self, recurrence: str) -> bool:
        """Check if the pattern represents a recurring task."""
        return recurrence in {"daily", "weekly", "monthly"}


# Singleton instance
_recurrence_calculator: Optional[RecurrenceCalculator] = None


def get_recurrence_calculator() -> RecurrenceCalculator:
    """Get singleton RecurrenceCalculator instance."""
    global _recurrence_calculator
    if _recurrence_calculator is None:
        _recurrence_calculator = RecurrenceCalculator()
    return _recurrence_calculator
