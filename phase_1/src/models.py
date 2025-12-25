"""
Task Model - Phase I Todo Application

Defines the Task dataclass representing a single todo item.
Use UV virtual environment for Python 3.13+ dependencies.

Maps to:
    - FR-002: Auto-generate unique, sequential integer IDs
    - FR-004: Capture creation timestamp
    - FR-005: Title (required, max 100 chars), description (optional, max 500 chars)
    - FR-006: Track status as Complete/Incomplete
    - IFR-001: Priority levels (High/Medium/Low)
    - IFR-002: Tags/categories for task organization
    - AFR-001: Recurring tasks (daily/weekly/monthly)
    - AFR-002: Due dates for tasks
    - AFR-003: Reminder notifications
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class Priority(Enum):
    """
    Task priority levels for organization and sorting.

    Attributes:
        HIGH: Urgent tasks that need immediate attention (value: 1 for sorting)
        MEDIUM: Normal priority tasks (value: 2 for sorting)
        LOW: Tasks that can be deferred (value: 3 for sorting)

    Example:
        task.priority = Priority.HIGH
        sorted_tasks = sorted(tasks, key=lambda t: t.priority.value)
    """
    HIGH = 1
    MEDIUM = 2
    LOW = 3

    def __str__(self) -> str:
        """Return human-readable priority name."""
        return self.name.capitalize()


# Valid tags for task categorization
VALID_TAGS = frozenset({"Work", "Home", "Personal", "Shopping", "Health", "Finance", "Learning"})


class Recurrence(Enum):
    """
    Task recurrence patterns for repeating tasks.

    Attributes:
        NONE: Task does not repeat (one-time task)
        DAILY: Task repeats every day
        WEEKLY: Task repeats every week
        MONTHLY: Task repeats every month

    Example:
        task.recurrence = Recurrence.WEEKLY
        # When completed, a new instance is created for next week

    Maps to: AFR-001
    """
    NONE = 0
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30  # Approximate, actual calculation uses calendar

    def __str__(self) -> str:
        """Return human-readable recurrence name."""
        if self == Recurrence.NONE:
            return "One-time"
        return self.name.capitalize()

    def get_next_due_date(self, from_date: datetime) -> datetime:
        """
        Calculate the next due date based on recurrence pattern.

        Args:
            from_date: The reference date to calculate from.

        Returns:
            The next due date for this recurrence pattern.

        Example:
            >>> recurrence = Recurrence.WEEKLY
            >>> next_date = recurrence.get_next_due_date(datetime.now())
        """
        if self == Recurrence.NONE:
            return from_date
        elif self == Recurrence.DAILY:
            return from_date + timedelta(days=1)
        elif self == Recurrence.WEEKLY:
            return from_date + timedelta(weeks=1)
        elif self == Recurrence.MONTHLY:
            # Add approximately one month (30 days)
            return from_date + timedelta(days=30)
        return from_date


@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-generated, sequential integer starting from 1).
             IDs are never reused after deletion.
        title: Brief name of the task (required, max 100 characters).
        description: Detailed information about the task (optional, max 500 characters).
        is_completed: Completion state (False = Incomplete, True = Complete).
                      Defaults to False for new tasks.
        created_at: Timestamp when the task was created.
                    Auto-generated at creation time.
        priority: Task priority level (High/Medium/Low).
                  Defaults to Medium for new tasks.
        tags: List of category tags for organization.
              Valid tags: Work, Home, Personal, Shopping, Health, Finance, Learning.
              Defaults to empty list.
        due_date: Optional deadline for the task.
                  None means no deadline. Used for reminders.
                  Maps to: AFR-002
        recurrence: Recurrence pattern for repeating tasks.
                    NONE = one-time, DAILY/WEEKLY/MONTHLY = repeating.
                    When a recurring task is completed, a new instance is created.
                    Maps to: AFR-001

    Display Format:
        Status indicators: [ ] for incomplete, [x] for complete
        Example: "[x] #1 [High] Buy groceries - Get milk and eggs (2025-12-24 10:30) [Work, Home]"
    """

    id: int
    title: str
    description: str = ""
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)
    due_date: datetime | None = None
    recurrence: Recurrence = Recurrence.NONE

    def __str__(self) -> str:
        """
        Format task for console display with status indicator.

        Returns:
            Formatted string with status, ID, priority, title, description preview,
            timestamp, and tags.
            Status indicators: [ ] incomplete, [x] complete (FR-007)
        """
        status = "[x]" if self.is_completed else "[ ]"
        priority_str = f"[{self.priority}]"
        desc_preview = (
            f" - {self.description[:50]}..."
            if len(self.description) > 50
            else f" - {self.description}" if self.description else ""
        )
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M")
        tags_str = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"{status} #{self.id} {priority_str} {self.title}{desc_preview} ({timestamp}){tags_str}"

    def status_text(self) -> str:
        """Return human-readable status text."""
        return "Complete" if self.is_completed else "Incomplete"

    def matches_keyword(self, keyword: str) -> bool:
        """
        Check if task matches a search keyword.

        Args:
            keyword: The search term to match (case-insensitive).

        Returns:
            True if keyword is found in title, description, or tags.
        """
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.title.lower()
            or keyword_lower in self.description.lower()
            or any(keyword_lower in tag.lower() for tag in self.tags)
        )
