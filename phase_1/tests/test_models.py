"""
Test Models Module - Phase I Todo Application

Pytest tests for Task, Priority, Recurrence models.
"""

import pytest
from datetime import datetime, timedelta

from src.models import Task, Priority, Recurrence, VALID_TAGS


class TestPriority:
    """Test Priority enum."""

    def test_priority_values(self):
        assert Priority.HIGH.value == 1
        assert Priority.MEDIUM.value == 2
        assert Priority.LOW.value == 3

    def test_priority_str(self):
        assert str(Priority.HIGH) == "High"
        assert str(Priority.MEDIUM) == "Medium"
        assert str(Priority.LOW) == "Low"

    def test_priority_sorting(self):
        priorities = [Priority.LOW, Priority.HIGH, Priority.MEDIUM]
        sorted_priorities = sorted(priorities, key=lambda p: p.value)
        assert sorted_priorities == [Priority.HIGH, Priority.MEDIUM, Priority.LOW]


class TestRecurrence:
    """Test Recurrence enum."""

    def test_recurrence_values(self):
        assert Recurrence.NONE.value == 0
        assert Recurrence.DAILY.value == 1
        assert Recurrence.WEEKLY.value == 7
        assert Recurrence.MONTHLY.value == 30

    def test_recurrence_str(self):
        assert str(Recurrence.NONE) == "One-time"
        assert str(Recurrence.DAILY) == "Daily"
        assert str(Recurrence.WEEKLY) == "Weekly"
        assert str(Recurrence.MONTHLY) == "Monthly"

    def test_get_next_due_date_none(self):
        now = datetime.now()
        result = Recurrence.NONE.get_next_due_date(now)
        assert result == now

    def test_get_next_due_date_daily(self):
        now = datetime.now()
        result = Recurrence.DAILY.get_next_due_date(now)
        expected = now + timedelta(days=1)
        assert result.date() == expected.date()

    def test_get_next_due_date_weekly(self):
        now = datetime.now()
        result = Recurrence.WEEKLY.get_next_due_date(now)
        expected = now + timedelta(weeks=1)
        assert result.date() == expected.date()

    def test_get_next_due_date_monthly(self):
        now = datetime.now()
        result = Recurrence.MONTHLY.get_next_due_date(now)
        expected = now + timedelta(days=30)
        assert result.date() == expected.date()


class TestValidTags:
    """Test VALID_TAGS constant."""

    def test_valid_tags_contains_expected(self):
        expected = ["Work", "Home", "Personal", "Shopping", "Health", "Finance", "Learning"]
        for tag in expected:
            assert tag in VALID_TAGS

    def test_valid_tags_is_frozenset(self):
        assert isinstance(VALID_TAGS, frozenset)


class TestTaskCreation:
    """Test Task creation."""

    def test_create_task_minimal(self):
        task = Task(id=1, title="Test Task")
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.is_completed == False
        assert task.priority == Priority.MEDIUM
        assert task.tags == []
        assert task.due_date is None
        assert task.recurrence == Recurrence.NONE

    def test_create_task_full(self):
        now = datetime.now()
        due = now + timedelta(days=7)
        task = Task(
            id=1,
            title="Full Task",
            description="Description",
            is_completed=True,
            created_at=now,
            priority=Priority.HIGH,
            tags=["Work", "Home"],
            due_date=due,
            recurrence=Recurrence.WEEKLY,
        )
        assert task.priority == Priority.HIGH
        assert task.tags == ["Work", "Home"]
        assert task.recurrence == Recurrence.WEEKLY


class TestTaskMethods:
    """Test Task methods."""

    def test_status_text(self):
        task1 = Task(id=1, title="Test", is_completed=False)
        task2 = Task(id=2, title="Test", is_completed=True)
        assert task1.status_text() == "Incomplete"
        assert task2.status_text() == "Complete"

    def test_matches_keyword_title(self):
        task = Task(id=1, title="Buy groceries")
        assert task.matches_keyword("groceries") == True
        assert task.matches_keyword("GROCERIES") == True

    def test_matches_keyword_description(self):
        task = Task(id=1, title="Shopping", description="Get milk")
        assert task.matches_keyword("milk") == True

    def test_matches_keyword_tags(self):
        task = Task(id=1, title="Task", tags=["Work", "Home"])
        assert task.matches_keyword("work") == True

    def test_matches_keyword_no_match(self):
        task = Task(id=1, title="Test")
        assert task.matches_keyword("xyz") == False

    def test_str_format(self):
        task = Task(id=1, title="Test", priority=Priority.HIGH)
        result = str(task)
        assert "[ ]" in result
        assert "#1" in result
        assert "Test" in result
