"""
Test Menu Module - Phase I Todo Application

Pytest tests for menu validation and input helpers.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.menu import (
    validate_menu_choice,
    validate_task_id,
    sanitize_title,
    sanitize_description,
    get_priority_choice,
    get_tags_input,
    get_recurrence_choice,
    get_due_date_input,
)
from src.models import Priority, Recurrence
from src.storage import TaskStorage
from src import MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH


# =============================================================================
# Tests for validate_menu_choice
# =============================================================================

class TestValidateMenuChoice:
    """Test validate_menu_choice function."""

    def test_valid_digits(self):
        """Test valid digit choices 0-9."""
        for i in range(10):
            is_valid, error = validate_menu_choice(str(i))
            assert is_valid == True
            assert error == ""

    def test_valid_voice_option(self):
        """Test 'V' is valid for voice command."""
        is_valid, error = validate_menu_choice("V")
        assert is_valid == True
        assert error == ""

    def test_valid_voice_lowercase(self):
        """Test 'v' is also valid."""
        is_valid, error = validate_menu_choice("v")
        assert is_valid == True

    def test_invalid_empty(self):
        """Test empty input is invalid."""
        is_valid, error = validate_menu_choice("")
        assert is_valid == False
        assert "choice" in error.lower()

    def test_invalid_whitespace(self):
        """Test whitespace-only is invalid."""
        is_valid, error = validate_menu_choice("   ")
        assert is_valid == False

    def test_invalid_letter(self):
        """Test non-V letters are invalid."""
        is_valid, error = validate_menu_choice("x")
        assert is_valid == False

    def test_invalid_number_out_of_range(self):
        """Test numbers > 9 are invalid."""
        is_valid, error = validate_menu_choice("10")
        assert is_valid == False

    def test_trims_whitespace(self):
        """Test whitespace is trimmed."""
        is_valid, error = validate_menu_choice("  5  ")
        assert is_valid == True


# =============================================================================
# Tests for validate_task_id
# =============================================================================

class TestValidateTaskId:
    """Test validate_task_id function."""

    def test_valid_positive_int(self):
        """Test valid positive integer."""
        is_valid, task_id, error = validate_task_id("5")
        assert is_valid == True
        assert task_id == 5
        assert error == ""

    def test_valid_large_number(self):
        """Test valid large number."""
        is_valid, task_id, error = validate_task_id("999")
        assert is_valid == True
        assert task_id == 999

    def test_invalid_empty(self):
        """Test empty input."""
        is_valid, task_id, error = validate_task_id("")
        assert is_valid == False
        assert task_id == 0

    def test_invalid_zero(self):
        """Test zero is invalid."""
        is_valid, task_id, error = validate_task_id("0")
        assert is_valid == False
        assert "positive" in error.lower()

    def test_invalid_negative(self):
        """Test negative number."""
        is_valid, task_id, error = validate_task_id("-5")
        assert is_valid == False

    def test_invalid_non_numeric(self):
        """Test non-numeric input."""
        is_valid, task_id, error = validate_task_id("abc")
        assert is_valid == False
        assert "valid number" in error.lower()

    def test_trims_whitespace(self):
        """Test whitespace is trimmed."""
        is_valid, task_id, error = validate_task_id("  10  ")
        assert is_valid == True
        assert task_id == 10


# =============================================================================
# Tests for sanitize_title
# =============================================================================

class TestSanitizeTitle:
    """Test sanitize_title function."""

    def test_normal_title(self):
        """Test normal title passes through."""
        title, warning = sanitize_title("Buy groceries")
        assert title == "Buy groceries"
        assert warning == ""

    def test_trims_whitespace(self):
        """Test whitespace is trimmed."""
        title, warning = sanitize_title("  Test  ")
        assert title == "Test"
        assert warning == ""

    def test_truncates_long_title(self):
        """Test long title is truncated."""
        long_title = "A" * (MAX_TITLE_LENGTH + 50)
        title, warning = sanitize_title(long_title)
        assert len(title) == MAX_TITLE_LENGTH
        assert "truncated" in warning.lower()

    def test_empty_returns_empty(self):
        """Test empty input returns empty."""
        title, warning = sanitize_title("")
        assert title == ""
        assert warning == ""


# =============================================================================
# Tests for sanitize_description
# =============================================================================

class TestSanitizeDescription:
    """Test sanitize_description function."""

    def test_normal_description(self):
        """Test normal description passes through."""
        desc, warning = sanitize_description("A description")
        assert desc == "A description"
        assert warning == ""

    def test_trims_whitespace(self):
        """Test whitespace is trimmed."""
        desc, warning = sanitize_description("  Test  ")
        assert desc == "Test"

    def test_truncates_long_description(self):
        """Test long description is truncated."""
        long_desc = "B" * (MAX_DESCRIPTION_LENGTH + 100)
        desc, warning = sanitize_description(long_desc)
        assert len(desc) == MAX_DESCRIPTION_LENGTH
        assert "truncated" in warning.lower()


# =============================================================================
# Tests for get_priority_choice (with mocking)
# =============================================================================

class TestGetPriorityChoice:
    """Test get_priority_choice with mocked input."""

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_priority_menu')
    def test_select_high(self, mock_menu, mock_input):
        """Test selecting high priority."""
        mock_input.return_value = "1"
        result = get_priority_choice()
        assert result == Priority.HIGH

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_priority_menu')
    def test_select_medium(self, mock_menu, mock_input):
        """Test selecting medium priority."""
        mock_input.return_value = "2"
        result = get_priority_choice()
        assert result == Priority.MEDIUM

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_priority_menu')
    def test_select_low(self, mock_menu, mock_input):
        """Test selecting low priority."""
        mock_input.return_value = "3"
        result = get_priority_choice()
        assert result == Priority.LOW

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_priority_menu')
    def test_default_medium(self, mock_menu, mock_input):
        """Test empty input defaults to medium."""
        mock_input.return_value = ""
        result = get_priority_choice()
        assert result == Priority.MEDIUM


# =============================================================================
# Tests for get_tags_input (with mocking)
# =============================================================================

class TestGetTagsInput:
    """Test get_tags_input with mocked input."""

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_tags_menu')
    def test_valid_tags(self, mock_menu, mock_input):
        """Test valid tags are returned."""
        mock_input.return_value = "Work, Home"
        result = get_tags_input()
        assert "Work" in result
        assert "Home" in result

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_tags_menu')
    def test_empty_returns_empty_list(self, mock_menu, mock_input):
        """Test empty input returns empty list."""
        mock_input.return_value = ""
        result = get_tags_input()
        assert result == []

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_tags_menu')
    @patch('src.menu.print_warning')
    def test_filters_invalid_tags(self, mock_warn, mock_menu, mock_input):
        """Test invalid tags are filtered and warned."""
        mock_input.return_value = "Work, InvalidTag"
        result = get_tags_input()
        assert "Work" in result
        assert "InvalidTag" not in result
        assert "Invalidtag" not in result


# =============================================================================
# Tests for get_recurrence_choice (with mocking)
# =============================================================================

class TestGetRecurrenceChoice:
    """Test get_recurrence_choice with mocked input."""

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_recurrence_menu')
    def test_select_none(self, mock_menu, mock_input):
        """Test selecting no recurrence."""
        mock_input.return_value = "1"
        result = get_recurrence_choice()
        assert result == Recurrence.NONE

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_recurrence_menu')
    def test_select_daily(self, mock_menu, mock_input):
        """Test selecting daily."""
        mock_input.return_value = "2"
        result = get_recurrence_choice()
        assert result == Recurrence.DAILY

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_recurrence_menu')
    def test_select_weekly(self, mock_menu, mock_input):
        """Test selecting weekly."""
        mock_input.return_value = "3"
        result = get_recurrence_choice()
        assert result == Recurrence.WEEKLY

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_recurrence_menu')
    def test_select_monthly(self, mock_menu, mock_input):
        """Test selecting monthly."""
        mock_input.return_value = "4"
        result = get_recurrence_choice()
        assert result == Recurrence.MONTHLY

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_recurrence_menu')
    def test_default_none(self, mock_menu, mock_input):
        """Test empty defaults to none."""
        mock_input.return_value = ""
        result = get_recurrence_choice()
        assert result == Recurrence.NONE


# =============================================================================
# Tests for get_due_date_input (with mocking)
# =============================================================================

class TestGetDueDateInput:
    """Test get_due_date_input with mocked input."""

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_due_date_prompt')
    def test_empty_returns_none(self, mock_prompt, mock_input):
        """Test empty input returns None."""
        mock_input.return_value = ""
        result = get_due_date_input()
        assert result is None

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_due_date_prompt')
    def test_valid_date_with_time(self, mock_prompt, mock_input):
        """Test valid date with time."""
        mock_input.return_value = "2025-12-25 14:30"
        result = get_due_date_input()
        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 14
        assert result.minute == 30

    @patch('src.menu.prompt_input')
    @patch('src.menu.display_due_date_prompt')
    def test_valid_date_only(self, mock_prompt, mock_input):
        """Test valid date without time."""
        mock_input.return_value = "2025-12-25"
        result = get_due_date_input()
        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 23  # Default end of day
        assert result.minute == 59
