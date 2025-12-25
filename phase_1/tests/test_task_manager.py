"""
Test Task Manager Module - Phase I Todo Application

Pytest tests for all task_manager functions.
"""

import pytest
from datetime import datetime, timedelta

from src.storage import TaskStorage
from src.models import Task, Priority, Recurrence
from src.task_manager import (
    list_tasks,
    get_task,
    add_task,
    toggle_completion,
    update_task,
    delete_task,
    search_tasks,
    filter_tasks,
    sort_tasks,
    update_task_priority,
    update_task_tags,
    update_task_due_date,
    update_task_recurrence,
    complete_recurring_task,
    get_due_tasks,
    get_overdue_tasks,
    get_upcoming_tasks,
    get_reminders,
)


@pytest.fixture
def storage():
    """Fresh storage for each test."""
    return TaskStorage()


@pytest.fixture
def storage_with_tasks(storage):
    """Storage with sample tasks."""
    add_task(storage, "Task 1", priority=Priority.HIGH, tags=["Work"])
    add_task(storage, "Task 2", priority=Priority.MEDIUM, tags=["Home"])
    add_task(storage, "Task 3", priority=Priority.LOW, tags=["Shopping"])
    return storage


# =============================================================================
# Basic CRUD Tests
# =============================================================================

class TestListTasks:
    """Test list_tasks function."""

    def test_empty(self, storage):
        assert list_tasks(storage) == []

    def test_returns_all(self, storage_with_tasks):
        result = list_tasks(storage_with_tasks)
        assert len(result) == 3


class TestGetTask:
    """Test get_task function."""

    def test_existing(self, storage_with_tasks):
        task = get_task(storage_with_tasks, 1)
        assert task is not None
        assert task.id == 1

    def test_nonexistent(self, storage):
        assert get_task(storage, 999) is None


class TestAddTask:
    """Test add_task function."""

    def test_add_simple(self, storage):
        task = add_task(storage, "New Task")
        assert task.id == 1
        assert task.title == "New Task"
        assert task.is_completed == False

    def test_add_with_options(self, storage):
        task = add_task(
            storage,
            "Full Task",
            description="Desc",
            priority=Priority.HIGH,
            tags=["Work"],
        )
        assert task.priority == Priority.HIGH
        assert "Work" in task.tags

    def test_add_trims_whitespace(self, storage):
        task = add_task(storage, "  Trimmed  ")
        assert task.title == "Trimmed"

    def test_add_empty_title_raises(self, storage):
        with pytest.raises(ValueError):
            add_task(storage, "")

    def test_add_whitespace_title_raises(self, storage):
        with pytest.raises(ValueError):
            add_task(storage, "   ")

    def test_add_filters_invalid_tags(self, storage):
        task = add_task(storage, "Task", tags=["Work", "InvalidTag", "Home"])
        assert "Work" in task.tags
        assert "Home" in task.tags
        assert "InvalidTag" not in task.tags

    def test_add_with_due_date(self, storage):
        due = datetime.now() + timedelta(days=7)
        task = add_task(storage, "Task", due_date=due)
        assert task.due_date == due

    def test_add_with_recurrence(self, storage):
        task = add_task(storage, "Task", recurrence=Recurrence.WEEKLY)
        assert task.recurrence == Recurrence.WEEKLY


class TestToggleCompletion:
    """Test toggle_completion function."""

    def test_toggle_incomplete_to_complete(self, storage):
        task = add_task(storage, "Task")
        result = toggle_completion(storage, task.id)
        assert result.is_completed == True

    def test_toggle_complete_to_incomplete(self, storage):
        task = add_task(storage, "Task")
        toggle_completion(storage, task.id)
        result = toggle_completion(storage, task.id)
        assert result.is_completed == False

    def test_toggle_nonexistent(self, storage):
        assert toggle_completion(storage, 999) is None


class TestUpdateTask:
    """Test update_task function."""

    def test_update_title(self, storage):
        task = add_task(storage, "Original")
        result = update_task(storage, task.id, title="Updated")
        assert result.title == "Updated"

    def test_update_description(self, storage):
        task = add_task(storage, "Task")
        result = update_task(storage, task.id, description="New desc")
        assert result.description == "New desc"

    def test_partial_update(self, storage):
        task = add_task(storage, "Task", description="Desc")
        result = update_task(storage, task.id, title="New Title")
        assert result.title == "New Title"
        assert result.description == "Desc"

    def test_update_nonexistent(self, storage):
        assert update_task(storage, 999, title="Nope") is None


class TestDeleteTask:
    """Test delete_task function."""

    def test_delete_existing(self, storage):
        task = add_task(storage, "Task")
        assert delete_task(storage, task.id) == True
        assert get_task(storage, task.id) is None

    def test_delete_nonexistent(self, storage):
        assert delete_task(storage, 999) == False


# =============================================================================
# Intermediate Features Tests
# =============================================================================

class TestSearchTasks:
    """Test search_tasks function."""

    def test_search_by_title(self, storage):
        add_task(storage, "Buy groceries")
        add_task(storage, "Work meeting")
        result = search_tasks(storage, "groceries")
        assert len(result) == 1
        assert result[0].title == "Buy groceries"

    def test_search_case_insensitive(self, storage):
        add_task(storage, "Buy MILK")
        result = search_tasks(storage, "milk")
        assert len(result) == 1

    def test_search_no_match(self, storage):
        add_task(storage, "Task")
        result = search_tasks(storage, "xyz")
        assert len(result) == 0

    def test_search_empty_keyword(self, storage_with_tasks):
        result = search_tasks(storage_with_tasks, "")
        assert len(result) == 3


class TestFilterTasks:
    """Test filter_tasks function."""

    def test_filter_by_status_incomplete(self, storage):
        add_task(storage, "Task 1")
        task2 = add_task(storage, "Task 2")
        toggle_completion(storage, task2.id)
        result = filter_tasks(storage, status=False)
        assert len(result) == 1

    def test_filter_by_status_complete(self, storage):
        task = add_task(storage, "Task")
        toggle_completion(storage, task.id)
        result = filter_tasks(storage, status=True)
        assert len(result) == 1

    def test_filter_by_priority(self, storage_with_tasks):
        result = filter_tasks(storage_with_tasks, priority=Priority.HIGH)
        assert len(result) == 1

    def test_filter_by_tag(self, storage_with_tasks):
        result = filter_tasks(storage_with_tasks, tag="Work")
        assert len(result) == 1

    def test_filter_combined(self, storage):
        add_task(storage, "Task", priority=Priority.HIGH, tags=["Work"])
        add_task(storage, "Task 2", priority=Priority.HIGH, tags=["Home"])
        result = filter_tasks(storage, priority=Priority.HIGH, tag="Work")
        assert len(result) == 1


class TestSortTasks:
    """Test sort_tasks function."""

    def test_sort_by_priority(self, storage_with_tasks):
        result = sort_tasks(storage_with_tasks, by="priority")
        assert result[0].priority == Priority.HIGH
        assert result[-1].priority == Priority.LOW

    def test_sort_by_title(self, storage):
        add_task(storage, "Zebra")
        add_task(storage, "Apple")
        add_task(storage, "Mango")
        result = sort_tasks(storage, by="title")
        assert result[0].title == "Apple"
        assert result[-1].title == "Zebra"

    def test_sort_by_created(self, storage_with_tasks):
        result = sort_tasks(storage_with_tasks, by="created")
        assert result[0].id < result[-1].id

    def test_sort_by_status(self, storage):
        task1 = add_task(storage, "Incomplete")
        task2 = add_task(storage, "Complete")
        toggle_completion(storage, task2.id)
        result = sort_tasks(storage, by="status")
        assert result[0].is_completed == False


class TestUpdateTaskPriority:
    """Test update_task_priority function."""

    def test_update_priority(self, storage):
        task = add_task(storage, "Task")
        result = update_task_priority(storage, task.id, Priority.HIGH)
        assert result.priority == Priority.HIGH

    def test_update_priority_nonexistent(self, storage):
        assert update_task_priority(storage, 999, Priority.HIGH) is None


class TestUpdateTaskTags:
    """Test update_task_tags function."""

    def test_update_tags(self, storage):
        task = add_task(storage, "Task")
        result = update_task_tags(storage, task.id, ["Work", "Home"])
        assert "Work" in result.tags
        assert "Home" in result.tags

    def test_update_tags_filters_invalid(self, storage):
        task = add_task(storage, "Task")
        result = update_task_tags(storage, task.id, ["Work", "Invalid"])
        assert "Work" in result.tags
        assert "Invalid" not in result.tags


# =============================================================================
# Advanced Features Tests
# =============================================================================

class TestUpdateTaskDueDate:
    """Test update_task_due_date function."""

    def test_set_due_date(self, storage):
        task = add_task(storage, "Task")
        due = datetime.now() + timedelta(days=7)
        result = update_task_due_date(storage, task.id, due)
        assert result.due_date == due

    def test_remove_due_date(self, storage):
        due = datetime.now() + timedelta(days=7)
        task = add_task(storage, "Task", due_date=due)
        result = update_task_due_date(storage, task.id, None)
        assert result.due_date is None


class TestUpdateTaskRecurrence:
    """Test update_task_recurrence function."""

    def test_set_recurrence(self, storage):
        task = add_task(storage, "Task")
        result = update_task_recurrence(storage, task.id, Recurrence.WEEKLY)
        assert result.recurrence == Recurrence.WEEKLY

    def test_remove_recurrence(self, storage):
        task = add_task(storage, "Task", recurrence=Recurrence.DAILY)
        result = update_task_recurrence(storage, task.id, Recurrence.NONE)
        assert result.recurrence == Recurrence.NONE


class TestCompleteRecurringTask:
    """Test complete_recurring_task function."""

    def test_complete_recurring_creates_new(self, storage):
        due = datetime.now()
        task = add_task(storage, "Recurring", due_date=due, recurrence=Recurrence.WEEKLY)
        completed, new_task = complete_recurring_task(storage, task.id)

        assert completed.is_completed == True
        assert new_task is not None
        assert new_task.is_completed == False
        assert new_task.recurrence == Recurrence.WEEKLY

    def test_complete_nonrecurring(self, storage):
        task = add_task(storage, "One-time")
        completed, new_task = complete_recurring_task(storage, task.id)

        assert completed.is_completed == True
        assert new_task is None

    def test_complete_nonexistent(self, storage):
        completed, new_task = complete_recurring_task(storage, 999)
        assert completed is None
        assert new_task is None


class TestDueDateQueries:
    """Test due date query functions."""

    def test_get_due_tasks(self, storage):
        # Due today
        today = datetime.now().replace(hour=23, minute=59)
        add_task(storage, "Due Today", due_date=today)
        # Due tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        add_task(storage, "Due Tomorrow", due_date=tomorrow)

        result = get_due_tasks(storage)
        assert len(result) == 1
        assert result[0].title == "Due Today"

    def test_get_overdue_tasks(self, storage):
        # Overdue
        yesterday = datetime.now() - timedelta(days=1)
        add_task(storage, "Overdue", due_date=yesterday)
        # Future
        tomorrow = datetime.now() + timedelta(days=1)
        add_task(storage, "Future", due_date=tomorrow)

        result = get_overdue_tasks(storage)
        assert len(result) == 1
        assert result[0].title == "Overdue"

    def test_get_upcoming_tasks(self, storage):
        # Within 7 days
        soon = datetime.now() + timedelta(days=3)
        add_task(storage, "Soon", due_date=soon)
        # After 7 days
        later = datetime.now() + timedelta(days=10)
        add_task(storage, "Later", due_date=later)

        result = get_upcoming_tasks(storage, days=7)
        assert len(result) == 1
        assert result[0].title == "Soon"


class TestGetReminders:
    """Test get_reminders function."""

    def test_reminders_structure(self, storage):
        result = get_reminders(storage)
        assert "overdue" in result
        assert "due_today" in result
        assert "due_soon" in result

    def test_reminders_categorizes(self, storage):
        # Overdue
        add_task(storage, "Overdue", due_date=datetime.now() - timedelta(days=1))
        # Today
        add_task(storage, "Today", due_date=datetime.now().replace(hour=23, minute=59))
        # Soon
        add_task(storage, "Soon", due_date=datetime.now() + timedelta(days=2))

        result = get_reminders(storage)
        assert len(result["overdue"]) == 1
        assert len(result["due_today"]) == 1
        assert len(result["due_soon"]) == 1
