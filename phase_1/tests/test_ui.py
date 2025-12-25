"""
Test UI Module - Phase I Todo Application

Pytest tests for UI display functions.
Note: Many UI functions use Rich library for display.
We test the logic, not the visual output.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.ui import (
    console,
    print_error,
    print_warning,
    print_success,
    print_info,
    prompt_confirm,
)
from src.models import Task, Priority, Recurrence


# =============================================================================
# Tests for print functions (verify they don't crash)
# =============================================================================

class TestPrintFunctions:
    """Test print functions execute without error."""

    def test_print_error(self, capsys):
        """Test print_error executes."""
        print_error("Test error")
        # Just verify no exception

    def test_print_warning(self, capsys):
        """Test print_warning executes."""
        print_warning("Test warning")
        # Just verify no exception

    def test_print_success(self, capsys):
        """Test print_success executes."""
        print_success("Test success")
        # Just verify no exception

    def test_print_info(self, capsys):
        """Test print_info executes."""
        print_info("Test info")
        # Just verify no exception


# =============================================================================
# Tests for prompt_confirm (with mocking)
# =============================================================================

class TestPromptConfirm:
    """Test prompt_confirm function."""

    @patch.object(console, 'input', return_value='y')
    def test_confirm_yes(self, mock_input):
        """Test 'y' returns True."""
        result = prompt_confirm("Confirm?")
        assert result == True

    @patch.object(console, 'input', return_value='Y')
    def test_confirm_yes_uppercase(self, mock_input):
        """Test 'Y' returns True."""
        result = prompt_confirm("Confirm?")
        assert result == True

    @patch.object(console, 'input', return_value='n')
    def test_confirm_no(self, mock_input):
        """Test 'n' returns False."""
        result = prompt_confirm("Confirm?")
        assert result == False

    @patch.object(console, 'input', return_value='N')
    def test_confirm_no_uppercase(self, mock_input):
        """Test 'N' returns False."""
        result = prompt_confirm("Confirm?")
        assert result == False


# =============================================================================
# Tests for Task display helpers
# =============================================================================

class TestTaskDisplay:
    """Test task-related display helpers."""

    def test_task_str_includes_status_incomplete(self):
        """Test incomplete task shows [ ]."""
        task = Task(id=1, title="Test", is_completed=False)
        assert "[ ]" in str(task)

    def test_task_str_includes_status_complete(self):
        """Test complete task shows [x]."""
        task = Task(id=1, title="Test", is_completed=True)
        assert "[x]" in str(task)

    def test_task_str_includes_id(self):
        """Test task string includes ID."""
        task = Task(id=42, title="Test")
        assert "#42" in str(task)

    def test_task_str_includes_title(self):
        """Test task string includes title."""
        task = Task(id=1, title="My Task Title")
        assert "My Task Title" in str(task)

    def test_task_str_includes_priority(self):
        """Test task string includes priority."""
        task = Task(id=1, title="Test", priority=Priority.HIGH)
        assert "High" in str(task)


# =============================================================================
# Tests for Priority display
# =============================================================================

class TestPriorityDisplay:
    """Test priority display."""

    def test_priority_high_str(self):
        """Test HIGH priority string."""
        assert str(Priority.HIGH) == "High"

    def test_priority_medium_str(self):
        """Test MEDIUM priority string."""
        assert str(Priority.MEDIUM) == "Medium"

    def test_priority_low_str(self):
        """Test LOW priority string."""
        assert str(Priority.LOW) == "Low"


# =============================================================================
# Tests for Recurrence display
# =============================================================================

class TestRecurrenceDisplay:
    """Test recurrence display."""

    def test_recurrence_none_str(self):
        """Test NONE recurrence string."""
        assert str(Recurrence.NONE) == "One-time"

    def test_recurrence_daily_str(self):
        """Test DAILY recurrence string."""
        assert str(Recurrence.DAILY) == "Daily"

    def test_recurrence_weekly_str(self):
        """Test WEEKLY recurrence string."""
        assert str(Recurrence.WEEKLY) == "Weekly"

    def test_recurrence_monthly_str(self):
        """Test MONTHLY recurrence string."""
        assert str(Recurrence.MONTHLY) == "Monthly"
