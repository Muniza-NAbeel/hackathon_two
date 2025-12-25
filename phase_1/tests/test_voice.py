"""
Test Voice Commands Module - Phase I Todo Application

Pytest tests for parse_voice_command and validate_voice_command skills.

Usage:
    cd phase_1
    pytest tests/test_voice.py -v

Maps to: VFR-001, VFR-002
"""

import pytest
from datetime import datetime, timedelta

from src.voice import (
    parse_voice_command,
    validate_voice_command,
    check_voice_available,
    _clean_command,
    _parse_priority,
    _parse_recurrence,
    _parse_tags,
    _parse_natural_date,
)
from src.models import Priority, Recurrence


# =============================================================================
# Tests for parse_voice_command skill
# =============================================================================

class TestParseVoiceCommandBasic:
    """Test basic voice commands: add, list, complete, delete."""

    def test_add_task_simple(self):
        """Test simple add task command."""
        action, args = parse_voice_command("Add task Buy milk")
        assert action == "add"
        assert args["title"] == "buy milk"

    def test_add_task_with_filler_words(self):
        """Test add task with filler words removed."""
        action, args = parse_voice_command("Um, please add task Buy groceries")
        assert action == "add"
        assert "buy groceries" in args["title"]

    def test_list_tasks(self):
        """Test list tasks command."""
        action, args = parse_voice_command("List tasks")
        assert action == "list"
        assert args == {}

    def test_show_tasks(self):
        """Test show tasks command (alias for list)."""
        action, args = parse_voice_command("Show all tasks")
        assert action == "list"

    def test_complete_task(self):
        """Test mark task complete command."""
        action, args = parse_voice_command("Mark task 5 complete")
        assert action == "complete"
        assert args["task_id"] == 5

    def test_complete_task_done_variant(self):
        """Test task done variant."""
        action, args = parse_voice_command("Task 3 done")
        assert action == "complete"
        assert args["task_id"] == 3

    def test_delete_task(self):
        """Test delete task command."""
        action, args = parse_voice_command("Delete task 2")
        assert action == "delete"
        assert args["task_id"] == 2


class TestParseVoiceCommandIntermediate:
    """Test intermediate voice commands: priority, tags, search, sort, filter."""

    def test_add_task_with_priority(self):
        """Test add task with priority."""
        action, args = parse_voice_command("Add task Meeting with High priority")
        assert action == "add"
        assert args["priority"] == Priority.HIGH

    def test_add_task_with_tag(self):
        """Test add task with tag."""
        action, args = parse_voice_command("Add task Buy groceries in Shopping")
        assert action == "add"
        assert "Shopping" in args.get("tags", [])

    def test_add_task_with_priority_and_tag(self):
        """Test add task with both priority and tag."""
        action, args = parse_voice_command("Add task Project deadline with High priority in Work")
        assert action == "add"
        assert args["priority"] == Priority.HIGH
        assert "Work" in args.get("tags", [])

    def test_search_tasks(self):
        """Test search tasks command."""
        action, args = parse_voice_command("Search tasks groceries")
        assert action == "search"
        assert args["keyword"] == "groceries"

    def test_find_tasks(self):
        """Test find tasks command (alias for search)."""
        action, args = parse_voice_command("Find tasks meeting")
        assert action == "search"
        assert args["keyword"] == "meeting"

    def test_sort_by_priority(self):
        """Test sort tasks by priority."""
        action, args = parse_voice_command("Sort tasks by priority")
        assert action == "sort"
        assert args["by"] == "priority"

    def test_sort_by_title(self):
        """Test sort tasks by title."""
        action, args = parse_voice_command("Sort tasks by title")
        assert action == "sort"
        assert args["by"] == "title"

    def test_filter_by_status_complete(self):
        """Test filter tasks by complete status."""
        action, args = parse_voice_command("Filter tasks by status complete")
        assert action == "filter"
        assert args["status"] == True

    def test_filter_by_status_incomplete(self):
        """Test filter tasks by incomplete status."""
        action, args = parse_voice_command("Filter tasks by status incomplete")
        assert action == "filter"
        assert args["status"] == False

    def test_filter_by_priority(self):
        """Test filter tasks by priority."""
        action, args = parse_voice_command("Filter tasks by priority high")
        assert action == "filter"
        assert args["priority"] == Priority.HIGH

    def test_filter_by_tag(self):
        """Test filter tasks by tag."""
        action, args = parse_voice_command("Filter tasks by tag Work")
        assert action == "filter"
        assert args["tag"] == "Work"

    def test_update_task_priority(self):
        """Test update task priority command."""
        action, args = parse_voice_command("Update task 1 priority to high")
        assert action == "update_priority"
        assert args["task_id"] == 1
        assert args["priority"] == Priority.HIGH


class TestParseVoiceCommandAdvanced:
    """Test advanced voice commands: recurring, due dates."""

    def test_add_recurring_task_weekly(self):
        """Test add recurring task weekly."""
        action, args = parse_voice_command("Add recurring task Gym weekly")
        assert action == "add"
        assert args["title"] == "gym"
        assert args["recurrence"] == Recurrence.WEEKLY

    def test_add_recurring_task_daily(self):
        """Test add recurring task daily."""
        action, args = parse_voice_command("Add recurring task Standup daily")
        assert action == "add"
        assert args["recurrence"] == Recurrence.DAILY

    def test_add_recurring_task_monthly(self):
        """Test add recurring task monthly."""
        action, args = parse_voice_command("Add recurring task Pay bills monthly")
        assert action == "add"
        assert args["recurrence"] == Recurrence.MONTHLY

    def test_set_due_date_tomorrow(self):
        """Test set due date as tomorrow."""
        action, args = parse_voice_command("Set due date for task 1 as tomorrow")
        assert action == "update_due_date"
        assert args["task_id"] == 1
        assert args["due_date"] is not None
        # Should be approximately tomorrow
        expected = datetime.now() + timedelta(days=1)
        assert args["due_date"].date() == expected.date()

    def test_set_due_date_absolute(self):
        """Test set due date with absolute date."""
        action, args = parse_voice_command("Set due date for task 2 as 2025-12-31")
        assert action == "update_due_date"
        assert args["task_id"] == 2
        assert args["due_date"].year == 2025
        assert args["due_date"].month == 12
        assert args["due_date"].day == 31

    def test_update_recurrence(self):
        """Test update task recurrence."""
        action, args = parse_voice_command("Update task 3 recurrence to weekly")
        assert action == "update_recurrence"
        assert args["task_id"] == 3
        assert args["recurrence"] == Recurrence.WEEKLY


class TestParseVoiceCommandEdgeCases:
    """Test edge cases and unknown commands."""

    def test_empty_command(self):
        """Test empty command returns unknown."""
        action, args = parse_voice_command("")
        assert action == "unknown"

    def test_unknown_command(self):
        """Test unrecognized command."""
        action, args = parse_voice_command("Do something random")
        assert action == "unknown"

    def test_case_insensitive(self):
        """Test commands are case insensitive."""
        action1, _ = parse_voice_command("ADD TASK Test")
        action2, _ = parse_voice_command("add task Test")
        assert action1 == action2 == "add"


# =============================================================================
# Tests for validate_voice_command skill
# =============================================================================

class TestValidateVoiceCommand:
    """Test validate_voice_command skill."""

    def test_valid_add_command(self):
        """Test valid add command."""
        is_valid, error = validate_voice_command("add", {"title": "Buy milk"})
        assert is_valid == True
        assert error is None

    def test_invalid_add_missing_title(self):
        """Test invalid add command without title."""
        is_valid, error = validate_voice_command("add", {})
        assert is_valid == False
        assert "title" in error.lower()

    def test_invalid_add_empty_title(self):
        """Test invalid add command with empty title."""
        is_valid, error = validate_voice_command("add", {"title": ""})
        assert is_valid == False
        assert "empty" in error.lower()

    def test_valid_complete_command(self):
        """Test valid complete command."""
        is_valid, error = validate_voice_command("complete", {"task_id": 5})
        assert is_valid == True
        assert error is None

    def test_invalid_complete_missing_id(self):
        """Test invalid complete command without task_id."""
        is_valid, error = validate_voice_command("complete", {})
        assert is_valid == False
        assert "task_id" in error.lower()

    def test_invalid_complete_negative_id(self):
        """Test invalid complete command with negative id."""
        is_valid, error = validate_voice_command("complete", {"task_id": -1})
        assert is_valid == False
        assert "positive" in error.lower()

    def test_valid_delete_command(self):
        """Test valid delete command."""
        is_valid, error = validate_voice_command("delete", {"task_id": 3})
        assert is_valid == True

    def test_valid_search_command(self):
        """Test valid search command."""
        is_valid, error = validate_voice_command("search", {"keyword": "groceries"})
        assert is_valid == True

    def test_invalid_search_empty_keyword(self):
        """Test invalid search with empty keyword."""
        is_valid, error = validate_voice_command("search", {"keyword": ""})
        assert is_valid == False

    def test_valid_list_command(self):
        """Test valid list command (no required args)."""
        is_valid, error = validate_voice_command("list", {})
        assert is_valid == True

    def test_valid_sort_command(self):
        """Test valid sort command."""
        is_valid, error = validate_voice_command("sort", {"by": "priority"})
        assert is_valid == True

    def test_valid_filter_command(self):
        """Test valid filter command."""
        is_valid, error = validate_voice_command("filter", {"status": True})
        assert is_valid == True

    def test_unknown_action(self):
        """Test unknown action is invalid."""
        is_valid, error = validate_voice_command("unknown", {})
        assert is_valid == False
        assert "unknown" in error.lower()

    def test_valid_update_priority(self):
        """Test valid update priority command."""
        is_valid, error = validate_voice_command(
            "update_priority",
            {"task_id": 1, "priority": Priority.HIGH}
        )
        assert is_valid == True

    def test_valid_update_due_date(self):
        """Test valid update due date command."""
        is_valid, error = validate_voice_command(
            "update_due_date",
            {"task_id": 1, "due_date": datetime.now()}
        )
        assert is_valid == True


# =============================================================================
# Tests for helper functions
# =============================================================================

class TestHelperFunctions:
    """Test internal helper functions."""

    def test_clean_command_removes_fillers(self):
        """Test filler words are removed."""
        result = _clean_command("Um, like, please add task")
        assert "um" not in result
        assert "like" not in result
        assert "please" not in result

    def test_parse_priority(self):
        """Test priority parsing."""
        assert _parse_priority("high") == Priority.HIGH
        assert _parse_priority("MEDIUM") == Priority.MEDIUM
        assert _parse_priority("Low") == Priority.LOW
        assert _parse_priority("invalid") == Priority.MEDIUM  # default

    def test_parse_recurrence(self):
        """Test recurrence parsing."""
        assert _parse_recurrence("daily") == Recurrence.DAILY
        assert _parse_recurrence("WEEKLY") == Recurrence.WEEKLY
        assert _parse_recurrence("monthly") == Recurrence.MONTHLY
        assert _parse_recurrence("none") == Recurrence.NONE

    def test_parse_tags_valid(self):
        """Test valid tags parsing."""
        tags = _parse_tags("Work, Home, Shopping")
        assert "Work" in tags
        assert "Home" in tags
        assert "Shopping" in tags

    def test_parse_tags_filters_invalid(self):
        """Test invalid tags are filtered out."""
        tags = _parse_tags("Work, InvalidTag, Home")
        assert "Work" in tags
        assert "Home" in tags
        assert "InvalidTag" not in tags
        assert "Invalidtag" not in tags

    def test_parse_natural_date_tomorrow(self):
        """Test natural date 'tomorrow'."""
        result = _parse_natural_date("tomorrow")
        expected = datetime.now() + timedelta(days=1)
        assert result.date() == expected.date()

    def test_parse_natural_date_next_week(self):
        """Test natural date 'next week'."""
        result = _parse_natural_date("next week")
        expected = datetime.now() + timedelta(weeks=1)
        assert result.date() == expected.date()

    def test_parse_natural_date_in_days(self):
        """Test natural date 'in X days'."""
        result = _parse_natural_date("in 3 days")
        expected = datetime.now() + timedelta(days=3)
        assert result.date() == expected.date()

    def test_parse_natural_date_absolute(self):
        """Test absolute date parsing."""
        result = _parse_natural_date("2025-12-25")
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 25

    def test_parse_natural_date_with_time(self):
        """Test absolute date with time."""
        result = _parse_natural_date("2025-12-25 14:30")
        assert result.year == 2025
        assert result.hour == 14
        assert result.minute == 30


# =============================================================================
# Tests for check_voice_available
# =============================================================================

class TestCheckVoiceAvailable:
    """Test voice availability check."""

    def test_returns_boolean(self):
        """Test that check_voice_available returns a boolean."""
        result = check_voice_available()
        assert isinstance(result, bool)
