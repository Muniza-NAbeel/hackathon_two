"""
Test Storage Module - Phase I Todo Application

Pytest tests for TaskStorage class.
"""

import pytest
from src.storage import TaskStorage
from src.models import Task, Priority


@pytest.fixture
def storage():
    """Fresh TaskStorage for each test."""
    return TaskStorage()


@pytest.fixture
def storage_with_tasks(storage):
    """Storage with pre-existing tasks."""
    for i in range(1, 4):
        task = Task(id=storage.next_id(), title=f"Task {i}")
        storage.create(task)
    return storage


class TestTaskStorageInit:
    """Test initialization."""

    def test_init_empty(self, storage):
        assert storage.count() == 0
        assert storage.is_empty() == True

    def test_next_id_starts_at_1(self, storage):
        assert storage.next_id() == 1


class TestNextId:
    """Test next_id method."""

    def test_increments(self, storage):
        assert storage.next_id() == 1
        assert storage.next_id() == 2
        assert storage.next_id() == 3

    def test_never_reused(self, storage):
        task = Task(id=storage.next_id(), title="Test")
        storage.create(task)
        storage.delete(task.id)
        assert storage.next_id() == 2


class TestCreate:
    """Test create method."""

    def test_create_single(self, storage):
        task = Task(id=storage.next_id(), title="Test")
        result = storage.create(task)
        assert result == task
        assert storage.count() == 1

    def test_create_multiple(self, storage):
        for i in range(5):
            storage.create(Task(id=storage.next_id(), title=f"Task {i}"))
        assert storage.count() == 5


class TestRead:
    """Test read method."""

    def test_read_existing(self, storage_with_tasks):
        task = storage_with_tasks.read(1)
        assert task is not None
        assert task.id == 1

    def test_read_nonexistent(self, storage):
        assert storage.read(999) is None

    def test_read_after_delete(self, storage):
        task = Task(id=storage.next_id(), title="Test")
        storage.create(task)
        storage.delete(task.id)
        assert storage.read(task.id) is None


class TestReadAll:
    """Test read_all method."""

    def test_empty(self, storage):
        assert storage.read_all() == []

    def test_returns_all(self, storage_with_tasks):
        result = storage_with_tasks.read_all()
        assert len(result) == 3

    def test_sorted_by_id(self, storage):
        storage.create(Task(id=3, title="Third"))
        storage.create(Task(id=1, title="First"))
        storage.create(Task(id=2, title="Second"))
        result = storage.read_all()
        assert [t.id for t in result] == [1, 2, 3]


class TestUpdate:
    """Test update method."""

    def test_update_existing(self, storage):
        task = Task(id=storage.next_id(), title="Original")
        storage.create(task)
        task.title = "Updated"
        result = storage.update(task)
        assert result.title == "Updated"

    def test_update_nonexistent(self, storage):
        task = Task(id=999, title="Nope")
        assert storage.update(task) is None

    def test_update_persists(self, storage):
        task = Task(id=storage.next_id(), title="Original")
        storage.create(task)
        task.title = "Updated"
        storage.update(task)
        assert storage.read(task.id).title == "Updated"


class TestDelete:
    """Test delete method."""

    def test_delete_existing(self, storage_with_tasks):
        assert storage_with_tasks.delete(1) == True
        assert storage_with_tasks.count() == 2

    def test_delete_nonexistent(self, storage):
        assert storage.delete(999) == False

    def test_delete_removes(self, storage):
        task = Task(id=storage.next_id(), title="Test")
        storage.create(task)
        storage.delete(task.id)
        assert storage.read(task.id) is None


class TestCountAndIsEmpty:
    """Test count and is_empty."""

    def test_count_empty(self, storage):
        assert storage.count() == 0

    def test_count_with_tasks(self, storage_with_tasks):
        assert storage_with_tasks.count() == 3

    def test_is_empty_true(self, storage):
        assert storage.is_empty() == True

    def test_is_empty_false(self, storage_with_tasks):
        assert storage_with_tasks.is_empty() == False
