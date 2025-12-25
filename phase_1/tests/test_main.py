"""
Test Main Module - Phase I Todo Application

Integration tests for main application flow.
Uses mocking to simulate user input.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import sys

from src.storage import TaskStorage
from src.models import Task, Priority, Recurrence
from src.task_manager import add_task, list_tasks


# =============================================================================
# Tests for Application Flow
# =============================================================================

class TestApplicationFlow:
    """Test main application flow."""

    @pytest.fixture
    def storage(self):
        """Fresh storage for each test."""
        return TaskStorage()

    def test_storage_initialization(self, storage):
        """Test storage starts empty."""
        assert storage.is_empty() == True
        assert storage.count() == 0

    def test_add_and_list_flow(self, storage):
        """Test adding and listing tasks."""
        # Add tasks
        task1 = add_task(storage, "Task 1")
        task2 = add_task(storage, "Task 2")

        # List tasks
        tasks = list_tasks(storage)

        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_complete_workflow(self, storage):
        """Test complete task workflow."""
        from src.task_manager import toggle_completion, get_task

        # Add task
        task = add_task(storage, "Complete me")
        assert task.is_completed == False

        # Complete task
        toggle_completion(storage, task.id)

        # Verify
        updated = get_task(storage, task.id)
        assert updated.is_completed == True

    def test_delete_workflow(self, storage):
        """Test delete task workflow."""
        from src.task_manager import delete_task, get_task

        # Add task
        task = add_task(storage, "Delete me")
        task_id = task.id

        # Delete task
        result = delete_task(storage, task_id)

        assert result == True
        assert get_task(storage, task_id) is None

    def test_search_workflow(self, storage):
        """Test search tasks workflow."""
        from src.task_manager import search_tasks

        # Add tasks
        add_task(storage, "Buy groceries")
        add_task(storage, "Work meeting")
        add_task(storage, "Buy milk")

        # Search
        results = search_tasks(storage, "buy")

        assert len(results) == 2

    def test_filter_workflow(self, storage):
        """Test filter tasks workflow."""
        from src.task_manager import filter_tasks, toggle_completion

        # Add tasks with different priorities
        task1 = add_task(storage, "High priority", priority=Priority.HIGH)
        task2 = add_task(storage, "Low priority", priority=Priority.LOW)
        toggle_completion(storage, task2.id)

        # Filter by priority
        high_tasks = filter_tasks(storage, priority=Priority.HIGH)
        assert len(high_tasks) == 1
        assert high_tasks[0].priority == Priority.HIGH

        # Filter by status
        complete_tasks = filter_tasks(storage, status=True)
        assert len(complete_tasks) == 1

    def test_sort_workflow(self, storage):
        """Test sort tasks workflow."""
        from src.task_manager import sort_tasks

        # Add tasks with different priorities
        add_task(storage, "Low task", priority=Priority.LOW)
        add_task(storage, "High task", priority=Priority.HIGH)
        add_task(storage, "Medium task", priority=Priority.MEDIUM)

        # Sort by priority
        sorted_tasks = sort_tasks(storage, by="priority")

        assert sorted_tasks[0].priority == Priority.HIGH
        assert sorted_tasks[1].priority == Priority.MEDIUM
        assert sorted_tasks[2].priority == Priority.LOW

    def test_recurring_task_workflow(self, storage):
        """Test recurring task workflow."""
        from src.task_manager import complete_recurring_task
        from datetime import datetime

        # Add recurring task
        due = datetime.now()
        task = add_task(
            storage,
            "Weekly task",
            due_date=due,
            recurrence=Recurrence.WEEKLY
        )

        # Complete recurring task
        completed, new_task = complete_recurring_task(storage, task.id)

        assert completed.is_completed == True
        assert new_task is not None
        assert new_task.is_completed == False
        assert new_task.recurrence == Recurrence.WEEKLY

    def test_reminders_workflow(self, storage):
        """Test reminders workflow."""
        from src.task_manager import get_reminders
        from datetime import datetime, timedelta

        # Add overdue task
        yesterday = datetime.now() - timedelta(days=1)
        add_task(storage, "Overdue task", due_date=yesterday)

        # Add task due today
        today = datetime.now().replace(hour=23, minute=59)
        add_task(storage, "Due today", due_date=today)

        # Get reminders
        reminders = get_reminders(storage)

        assert len(reminders["overdue"]) == 1
        assert len(reminders["due_today"]) == 1


# =============================================================================
# Tests for Voice Command Integration
# =============================================================================

class TestVoiceCommandIntegration:
    """Test voice command integration."""

    def test_parse_add_command(self):
        """Test parsing add command."""
        from src.voice import parse_voice_command, validate_voice_command

        action, args = parse_voice_command("Add task Buy groceries")
        is_valid, error = validate_voice_command(action, args)

        assert action == "add"
        assert is_valid == True
        assert "title" in args

    def test_parse_complete_command(self):
        """Test parsing complete command."""
        from src.voice import parse_voice_command, validate_voice_command

        action, args = parse_voice_command("Mark task 5 complete")
        is_valid, error = validate_voice_command(action, args)

        assert action == "complete"
        assert is_valid == True
        assert args["task_id"] == 5

    def test_parse_search_command(self):
        """Test parsing search command."""
        from src.voice import parse_voice_command, validate_voice_command

        action, args = parse_voice_command("Search tasks groceries")
        is_valid, error = validate_voice_command(action, args)

        assert action == "search"
        assert is_valid == True
        assert args["keyword"] == "groceries"

    def test_voice_to_execution(self):
        """Test voice command to execution flow."""
        from src.voice import parse_voice_command, validate_voice_command
        from src.task_manager import add_task

        storage = TaskStorage()

        # Parse voice command
        action, args = parse_voice_command("Add task Test voice command")
        is_valid, _ = validate_voice_command(action, args)

        assert is_valid == True

        # Execute
        if action == "add":
            task = add_task(storage, args["title"])
            assert task is not None
            assert "test voice command" in task.title.lower()


# =============================================================================
# Tests for Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def storage(self):
        return TaskStorage()

    def test_empty_storage_operations(self, storage):
        """Test operations on empty storage."""
        from src.task_manager import list_tasks, search_tasks, filter_tasks

        assert list_tasks(storage) == []
        assert search_tasks(storage, "anything") == []
        assert filter_tasks(storage, status=True) == []

    def test_nonexistent_task_operations(self, storage):
        """Test operations on non-existent tasks."""
        from src.task_manager import get_task, toggle_completion, delete_task

        assert get_task(storage, 999) is None
        assert toggle_completion(storage, 999) is None
        assert delete_task(storage, 999) == False

    def test_invalid_voice_commands(self):
        """Test invalid voice commands."""
        from src.voice import parse_voice_command, validate_voice_command

        # Empty command
        action, args = parse_voice_command("")
        is_valid, error = validate_voice_command(action, args)
        assert is_valid == False

        # Unknown command
        action, args = parse_voice_command("Do something random")
        is_valid, error = validate_voice_command(action, args)
        assert is_valid == False

    def test_special_characters_in_title(self, storage):
        """Test special characters in task title."""
        task = add_task(storage, "Task with @#$%^& symbols!")
        assert task.title == "Task with @#$%^& symbols!"

    def test_unicode_in_title(self, storage):
        """Test unicode in task title."""
        task = add_task(storage, "Task with emoji 🎉 and urdu اردو")
        assert "🎉" in task.title
        assert "اردو" in task.title

    def test_max_length_title(self, storage):
        """Test maximum length title is truncated."""
        from src import MAX_TITLE_LENGTH

        long_title = "A" * 200
        task = add_task(storage, long_title)
        assert len(task.title) == MAX_TITLE_LENGTH


# =============================================================================
# Tests for Menu Choice Validation
# =============================================================================

class TestMenuValidation:
    """Test menu choice validation."""

    def test_all_valid_choices(self):
        """Test all valid menu choices."""
        from src.menu import validate_menu_choice

        valid_choices = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "V", "v"]
        for choice in valid_choices:
            is_valid, _ = validate_menu_choice(choice)
            assert is_valid == True, f"Choice '{choice}' should be valid"

    def test_invalid_choices(self):
        """Test invalid menu choices."""
        from src.menu import validate_menu_choice

        invalid_choices = ["", " ", "10", "abc", "x", "-1"]
        for choice in invalid_choices:
            is_valid, _ = validate_menu_choice(choice)
            assert is_valid == False, f"Choice '{choice}' should be invalid"
