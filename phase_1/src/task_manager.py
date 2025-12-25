"""
Task Manager - Phase I Todo Application

Core business logic functions for task operations.
Use UV virtual environment for Python 3.13+ dependencies.

All functions follow single-responsibility principle and are modular.
Functions are mapped to specific tasks and functional requirements.

Maps to:
    - FR-002: Auto-generate unique IDs
    - FR-004: Capture creation timestamp
    - FR-005: Title (max 100), description (max 500)
    - FR-006: Track completion status
    - FR-008: Validate task IDs before operations
    - FR-012: Trim whitespace from inputs
    - FR-013: Prevent empty titles
    - FR-015: Allow partial updates
    - IFR-001: Priority levels (High/Medium/Low)
    - IFR-002: Tags/categories for task organization
    - IFR-003: Search tasks by keyword
    - IFR-004: Filter tasks by status, priority, tag
    - IFR-005: Sort tasks by priority, title, or due date
"""

from datetime import datetime

from src import MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH
from src.models import Task, Priority, Recurrence, VALID_TAGS
from src.storage import TaskStorage


def list_tasks(storage: TaskStorage) -> list[Task]:
    """
    Retrieve all tasks from storage.

    Args:
        storage: The TaskStorage instance.

    Returns:
        List of all Task objects, sorted by ID.

    Maps to: FR-007, T012
    """
    return storage.read_all()


def get_task(storage: TaskStorage, task_id: int) -> Task | None:
    """
    Retrieve a single task by ID.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.

    Returns:
        The Task object if found, None otherwise.

    Maps to: FR-008, T018
    """
    return storage.read(task_id)


def add_task(
    storage: TaskStorage,
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    tags: list[str] | None = None,
    due_date: datetime | None = None,
    recurrence: Recurrence = Recurrence.NONE,
) -> Task:
    """
    Create a new task with auto-generated ID and timestamp.

    Args:
        storage: The TaskStorage instance.
        title: The task title (required, will be trimmed and truncated).
        description: The task description (optional, will be trimmed and truncated).
        priority: Task priority level (default: Medium).
        tags: List of category tags (default: empty list).
              Invalid tags are filtered out.
        due_date: Optional deadline for the task.
        recurrence: Recurrence pattern (NONE, DAILY, WEEKLY, MONTHLY).

    Returns:
        The created Task object.

    Raises:
        ValueError: If title is empty after trimming.

    Example:
        >>> task = add_task(storage, "Buy groceries", "Milk and eggs",
        ...                 priority=Priority.HIGH, tags=["Shopping", "Home"],
        ...                 due_date=datetime(2025, 12, 25), recurrence=Recurrence.WEEKLY)

    Maps to: FR-002, FR-004, FR-005, FR-006, FR-012, FR-013, IFR-001, IFR-002, AFR-001, AFR-002, T015
    """
    # Trim whitespace (FR-012)
    title = title.strip()
    description = description.strip()

    # Validate title not empty (FR-013)
    if not title:
        raise ValueError("Title cannot be empty.")

    # Truncate if needed (FR-005)
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH]
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[:MAX_DESCRIPTION_LENGTH]

    # Validate and filter tags (IFR-002)
    valid_tags = []
    if tags:
        for tag in tags:
            tag = tag.strip().capitalize()
            if tag in VALID_TAGS:
                valid_tags.append(tag)

    # Create task with auto-generated ID and timestamp (FR-002, FR-004)
    task = Task(
        id=storage.next_id(),
        title=title,
        description=description,
        is_completed=False,  # Default to incomplete (FR-006)
        created_at=datetime.now(),
        priority=priority,
        tags=valid_tags,
        due_date=due_date,
        recurrence=recurrence,
    )

    # Store and return
    return storage.create(task)


def toggle_completion(storage: TaskStorage, task_id: int) -> Task | None:
    """
    Toggle the completion status of a task.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.

    Returns:
        The updated Task object if found, None if not found.

    Maps to: FR-006, FR-008, T019
    """
    task = storage.read(task_id)
    if task is None:
        return None

    # Toggle the status
    task.is_completed = not task.is_completed

    # Update in storage
    return storage.update(task)


def update_task(
    storage: TaskStorage,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> Task | None:
    """
    Update a task's title and/or description.

    Supports partial updates: if a field is None, it is not changed.
    Empty strings for title are treated as "keep current" (partial update).

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.
        title: New title (None or empty = keep current).
        description: New description (None = keep current, empty string clears it).

    Returns:
        The updated Task object if found, None if not found.

    Maps to: FR-008, FR-012, FR-015, T022
    """
    task = storage.read(task_id)
    if task is None:
        return None

    # Update title if provided and not empty (FR-015)
    if title is not None:
        title = title.strip()  # FR-012
        if title:  # Only update if not empty (partial update)
            if len(title) > MAX_TITLE_LENGTH:
                title = title[:MAX_TITLE_LENGTH]
            task.title = title

    # Update description if provided (FR-015)
    # Note: Empty string is valid for description (clears it)
    if description is not None:
        description = description.strip()  # FR-012
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH]
        task.description = description

    # Update in storage
    return storage.update(task)


def delete_task(storage: TaskStorage, task_id: int) -> bool:
    """
    Delete a task by ID.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.

    Returns:
        True if deleted successfully, False if not found.

    Maps to: FR-008, T025
    """
    return storage.delete(task_id)


# =============================================================================
# Intermediate Features: Search, Filter, Sort (IFR-003, IFR-004, IFR-005)
# =============================================================================


def search_tasks(storage: TaskStorage, keyword: str) -> list[Task]:
    """
    Search tasks by keyword in title, description, or tags.

    Args:
        storage: The TaskStorage instance.
        keyword: The search term (case-insensitive).

    Returns:
        List of Task objects matching the keyword.

    Example:
        >>> results = search_tasks(storage, "groceries")
        >>> for task in results:
        ...     print(task)

    Maps to: IFR-003
    """
    if not keyword or not keyword.strip():
        return list_tasks(storage)

    keyword = keyword.strip()
    tasks = list_tasks(storage)
    return [task for task in tasks if task.matches_keyword(keyword)]


def filter_tasks(
    storage: TaskStorage,
    status: bool | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
) -> list[Task]:
    """
    Filter tasks by status, priority, and/or tag.

    Multiple filters are combined with AND logic.

    Args:
        storage: The TaskStorage instance.
        status: Filter by completion status (True=complete, False=incomplete, None=all).
        priority: Filter by priority level (None=all).
        tag: Filter by tag (case-insensitive, None=all).

    Returns:
        List of Task objects matching all specified filters.

    Example:
        >>> # Get all incomplete high-priority tasks
        >>> tasks = filter_tasks(storage, status=False, priority=Priority.HIGH)
        >>> # Get all tasks with "Work" tag
        >>> work_tasks = filter_tasks(storage, tag="Work")

    Maps to: IFR-004
    """
    tasks = list_tasks(storage)

    # Filter by status
    if status is not None:
        tasks = [task for task in tasks if task.is_completed == status]

    # Filter by priority
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]

    # Filter by tag (case-insensitive)
    if tag is not None:
        tag_lower = tag.strip().lower()
        tasks = [
            task for task in tasks
            if any(t.lower() == tag_lower for t in task.tags)
        ]

    return tasks


def sort_tasks(
    storage: TaskStorage,
    by: str = "priority",
    reverse: bool = False,
) -> list[Task]:
    """
    Sort tasks by specified criteria.

    Args:
        storage: The TaskStorage instance.
        by: Sort criteria - "priority", "title", "created", or "status".
            - "priority": Sort by priority (High -> Medium -> Low)
            - "title": Sort alphabetically by title
            - "created": Sort by creation date (oldest first)
            - "status": Sort by completion status (incomplete first)
        reverse: Reverse the sort order (default: False).

    Returns:
        List of Task objects sorted by the specified criteria.

    Example:
        >>> # Sort by priority (high first)
        >>> tasks = sort_tasks(storage, by="priority")
        >>> # Sort by title Z-A
        >>> tasks = sort_tasks(storage, by="title", reverse=True)

    Maps to: IFR-005
    """
    tasks = list_tasks(storage)

    if by == "priority":
        # Sort by priority value (1=High, 2=Medium, 3=Low)
        tasks.sort(key=lambda t: t.priority.value, reverse=reverse)
    elif by == "title":
        # Sort alphabetically by title (case-insensitive)
        tasks.sort(key=lambda t: t.title.lower(), reverse=reverse)
    elif by == "created":
        # Sort by creation timestamp
        tasks.sort(key=lambda t: t.created_at, reverse=reverse)
    elif by == "status":
        # Sort by completion status (incomplete=0, complete=1)
        tasks.sort(key=lambda t: t.is_completed, reverse=reverse)
    else:
        # Default: sort by ID
        tasks.sort(key=lambda t: t.id, reverse=reverse)

    return tasks


def update_task_priority(
    storage: TaskStorage,
    task_id: int,
    priority: Priority,
) -> Task | None:
    """
    Update a task's priority level.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.
        priority: The new priority level.

    Returns:
        The updated Task object if found, None if not found.

    Maps to: IFR-001
    """
    task = storage.read(task_id)
    if task is None:
        return None

    task.priority = priority
    return storage.update(task)


def update_task_tags(
    storage: TaskStorage,
    task_id: int,
    tags: list[str],
) -> Task | None:
    """
    Update a task's tags.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.
        tags: The new list of tags. Invalid tags are filtered out.

    Returns:
        The updated Task object if found, None if not found.

    Maps to: IFR-002
    """
    task = storage.read(task_id)
    if task is None:
        return None

    # Validate and filter tags
    valid_tags = []
    for tag in tags:
        tag = tag.strip().capitalize()
        if tag in VALID_TAGS:
            valid_tags.append(tag)

    task.tags = valid_tags
    return storage.update(task)


# =============================================================================
# Advanced Features: Recurring Tasks & Reminders (AFR-001, AFR-002, AFR-003)
# =============================================================================


def update_task_due_date(
    storage: TaskStorage,
    task_id: int,
    due_date: datetime | None,
) -> Task | None:
    """
    Update a task's due date.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.
        due_date: The new due date (None to remove deadline).

    Returns:
        The updated Task object if found, None if not found.

    Maps to: AFR-002
    """
    task = storage.read(task_id)
    if task is None:
        return None

    task.due_date = due_date
    return storage.update(task)


def update_task_recurrence(
    storage: TaskStorage,
    task_id: int,
    recurrence: Recurrence,
) -> Task | None:
    """
    Update a task's recurrence pattern.

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task.
        recurrence: The new recurrence pattern.

    Returns:
        The updated Task object if found, None if not found.

    Maps to: AFR-001
    """
    task = storage.read(task_id)
    if task is None:
        return None

    task.recurrence = recurrence
    return storage.update(task)


def complete_recurring_task(storage: TaskStorage, task_id: int) -> tuple[Task | None, Task | None]:
    """
    Complete a recurring task and create its next instance.

    When a recurring task is marked complete, this function:
    1. Marks the current task as completed
    2. If task has recurrence != NONE, creates a new incomplete task
       with the next due date calculated from the recurrence pattern

    Args:
        storage: The TaskStorage instance.
        task_id: The unique identifier of the task to complete.

    Returns:
        Tuple of (completed_task, new_task):
        - completed_task: The completed Task object (None if not found)
        - new_task: The new recurring Task instance (None if non-recurring)

    Example:
        >>> completed, new_instance = complete_recurring_task(storage, 1)
        >>> if new_instance:
        ...     print(f"Next instance created: {new_instance}")

    Maps to: AFR-001
    """
    task = storage.read(task_id)
    if task is None:
        return None, None

    # Mark the current task as completed
    task.is_completed = True
    completed_task = storage.update(task)

    # If non-recurring, just return the completed task
    if task.recurrence == Recurrence.NONE:
        return completed_task, None

    # Calculate next due date based on recurrence pattern
    reference_date = task.due_date if task.due_date else datetime.now()
    next_due_date = task.recurrence.get_next_due_date(reference_date)

    # Create new task instance for next occurrence
    new_task = Task(
        id=storage.next_id(),
        title=task.title,
        description=task.description,
        is_completed=False,
        created_at=datetime.now(),
        priority=task.priority,
        tags=task.tags.copy(),
        due_date=next_due_date,
        recurrence=task.recurrence,
    )

    new_task = storage.create(new_task)
    return completed_task, new_task


def get_due_tasks(storage: TaskStorage) -> list[Task]:
    """
    Get all incomplete tasks that are due today.

    Args:
        storage: The TaskStorage instance.

    Returns:
        List of incomplete Task objects due today.

    Example:
        >>> due_today = get_due_tasks(storage)
        >>> for task in due_today:
        ...     print(f"Due today: {task.title}")

    Maps to: AFR-002, AFR-003
    """
    tasks = list_tasks(storage)
    today = datetime.now().date()

    return [
        task for task in tasks
        if not task.is_completed
        and task.due_date is not None
        and task.due_date.date() == today
    ]


def get_overdue_tasks(storage: TaskStorage) -> list[Task]:
    """
    Get all incomplete tasks that are past their due date.

    Args:
        storage: The TaskStorage instance.

    Returns:
        List of incomplete Task objects that are overdue.

    Example:
        >>> overdue = get_overdue_tasks(storage)
        >>> for task in overdue:
        ...     print(f"OVERDUE: {task.title}")

    Maps to: AFR-002, AFR-003
    """
    tasks = list_tasks(storage)
    now = datetime.now()

    return [
        task for task in tasks
        if not task.is_completed
        and task.due_date is not None
        and task.due_date < now
    ]


def get_upcoming_tasks(storage: TaskStorage, days: int = 7) -> list[Task]:
    """
    Get all incomplete tasks due within the specified number of days.

    Args:
        storage: The TaskStorage instance.
        days: Number of days to look ahead (default: 7).

    Returns:
        List of incomplete Task objects due within the specified period,
        sorted by due date (earliest first).

    Example:
        >>> upcoming = get_upcoming_tasks(storage, days=3)
        >>> for task in upcoming:
        ...     print(f"Due soon: {task.title} - {task.due_date}")

    Maps to: AFR-002, AFR-003
    """
    from datetime import timedelta

    tasks = list_tasks(storage)
    now = datetime.now()
    future_limit = now + timedelta(days=days)

    upcoming = [
        task for task in tasks
        if not task.is_completed
        and task.due_date is not None
        and now <= task.due_date <= future_limit
    ]

    # Sort by due date (earliest first)
    upcoming.sort(key=lambda t: t.due_date)
    return upcoming


def get_reminders(storage: TaskStorage) -> dict[str, list[Task]]:
    """
    Get task reminders categorized by urgency.

    Returns a dictionary with categorized tasks:
    - 'overdue': Tasks past their due date
    - 'due_today': Tasks due today
    - 'due_soon': Tasks due within the next 3 days

    Args:
        storage: The TaskStorage instance.

    Returns:
        Dictionary with 'overdue', 'due_today', and 'due_soon' keys,
        each containing a list of matching Task objects.

    Example:
        >>> reminders = get_reminders(storage)
        >>> if reminders['overdue']:
        ...     print("You have overdue tasks!")
        >>> if reminders['due_today']:
        ...     print("Tasks due today!")

    Maps to: AFR-003
    """
    from datetime import timedelta

    tasks = list_tasks(storage)
    now = datetime.now()
    today = now.date()
    soon_limit = now + timedelta(days=3)

    overdue = []
    due_today = []
    due_soon = []

    for task in tasks:
        if task.is_completed or task.due_date is None:
            continue

        task_date = task.due_date.date()

        if task.due_date < now:
            overdue.append(task)
        elif task_date == today:
            due_today.append(task)
        elif now < task.due_date <= soon_limit:
            due_soon.append(task)

    return {
        'overdue': overdue,
        'due_today': due_today,
        'due_soon': due_soon,
    }
