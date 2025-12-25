"""
In-Memory Task Storage - Phase I Todo Application

Provides in-memory storage for Task objects using a dictionary.
Use UV virtual environment for Python 3.13+ dependencies.

Maps to:
    - FR-003: Store task data in memory only; data is not persisted between sessions.
    - FR-002: Auto-generate unique, sequential integer IDs starting from 1.

Future Persistence Note:
    This class can be extended to implement file-based or database persistence
    by replacing the internal dictionary with appropriate storage mechanisms.
    The public interface (create, read, read_all, update, delete) will remain unchanged.
"""

from src.models import Task


class TaskStorage:
    """
    In-memory storage for Task objects.

    Uses a dictionary internally for O(1) lookup by task ID.
    IDs are auto-incremented and never reused after deletion.

    Attributes:
        _tasks: Internal dictionary mapping task IDs to Task objects.
        _next_id: Counter for generating unique task IDs (starts at 1).

    Example:
        storage = TaskStorage()
        task = Task(id=storage.next_id(), title="Buy groceries")
        storage.create(task)
        all_tasks = storage.read_all()
    """

    def __init__(self) -> None:
        """Initialize empty storage with ID counter starting at 1."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def next_id(self) -> int:
        """
        Get the next available task ID and increment the counter.

        IDs are never reused, even after task deletion.
        This ensures referential integrity and prevents confusion.

        Returns:
            The next available unique integer ID.
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def create(self, task: Task) -> Task:
        """
        Add a new task to storage.

        Args:
            task: The Task object to store. Must have a unique ID.

        Returns:
            The stored Task object.

        Note:
            The task's ID should be obtained via next_id() before calling create().
        """
        self._tasks[task.id] = task
        return task

    def read(self, task_id: int) -> Task | None:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task to retrieve.

        Returns:
            The Task object if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def read_all(self) -> list[Task]:
        """
        Retrieve all tasks from storage.

        Returns:
            List of all Task objects, sorted by ID (ascending).
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(self, task: Task) -> Task | None:
        """
        Update an existing task in storage.

        Args:
            task: The Task object with updated values.
                  The task's ID must match an existing task.

        Returns:
            The updated Task object if found and updated, None if not found.
        """
        if task.id not in self._tasks:
            return None
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        """
        Remove a task from storage.

        Args:
            task_id: The unique identifier of the task to delete.

        Returns:
            True if the task was found and deleted, False if not found.

        Note:
            The task ID will not be reused for new tasks after deletion.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def count(self) -> int:
        """
        Get the total number of tasks in storage.

        Returns:
            The number of tasks currently stored.
        """
        return len(self._tasks)

    def is_empty(self) -> bool:
        """
        Check if storage is empty.

        Returns:
            True if no tasks are stored, False otherwise.
        """
        return len(self._tasks) == 0
