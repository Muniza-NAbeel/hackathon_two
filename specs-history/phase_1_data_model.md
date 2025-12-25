# Data Model: Todo In-Memory Console Application (Phase I)

**Feature**: Phase I Todo Console App
**Date**: 2025-12-24
**Status**: Complete

---

## Entity Overview

Phase I has a single entity with an in-memory storage abstraction.

```
┌─────────────────────────────────────────────────────────┐
│                      TaskStorage                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                    Task                          │   │
│  │  id: int                                         │   │
│  │  title: str                                      │   │
│  │  description: str                                │   │
│  │  is_completed: bool                              │   │
│  │  created_at: datetime                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  _tasks: dict[int, Task]                               │
│  _next_id: int                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Entity: Task

### Definition

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """
    Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-generated, never reused)
        title: Brief name of the task (required, max 100 chars)
        description: Detailed info about task (optional, max 500 chars)
        is_completed: Completion state (default: False)
        created_at: Timestamp when task was created (auto-generated)
    """
    id: int
    title: str
    description: str = ""
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

### Field Specifications

| Field | Type | Required | Default | Constraints | FR Reference |
|-------|------|----------|---------|-------------|--------------|
| `id` | `int` | Yes | Auto-generated | >= 1, unique, never reused | FR-002 |
| `title` | `str` | Yes | N/A | 1-100 chars after trim, non-empty | FR-005, FR-013 |
| `description` | `str` | No | `""` | 0-500 chars after trim | FR-005 |
| `is_completed` | `bool` | No | `False` | True or False | FR-006 |
| `created_at` | `datetime` | No | `datetime.now()` | Auto-set at creation | FR-004 |

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `title` | Cannot be empty after trim | "Title cannot be empty." |
| `title` | Max 100 characters | "Title truncated to 100 characters." (warning) |
| `description` | Max 500 characters | "Description truncated to 500 characters." (warning) |
| `id` | Must exist for operations | "Task #X not found." |

### State Transitions

```
                 ┌──────────────────────┐
                 │       CREATED        │
                 │  is_completed=False  │
                 └──────────┬───────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  UPDATE  │     │  TOGGLE  │     │  DELETE  │
    │  title/  │     │  status  │     │ (removed)│
    │   desc   │     │          │     └──────────┘
    └────┬─────┘     └────┬─────┘
         │                │
         │                ▼
         │         ┌──────────────────────┐
         │         │      COMPLETED       │
         │         │  is_completed=True   │
         │         └──────────┬───────────┘
         │                    │
         │                    ▼ (toggle again)
         │         ┌──────────────────────┐
         └────────►│      INCOMPLETE      │
                   │  is_completed=False  │
                   └──────────────────────┘
```

### Display Format

```python
def __str__(self) -> str:
    """Format task for console display."""
    status = "[x]" if self.is_completed else "[ ]"
    timestamp = self.created_at.strftime("%Y-%m-%d %H:%M")

    if len(self.description) > 50:
        desc_preview = f" - {self.description[:50]}..."
    elif self.description:
        desc_preview = f" - {self.description}"
    else:
        desc_preview = ""

    return f"{status} #{self.id}: {self.title}{desc_preview} (Created: {timestamp})"
```

**Examples**:
```
[ ] #1: Buy groceries - Get milk and bread (Created: 2025-12-24 10:30)
[x] #2: Call dentist (Created: 2025-12-24 09:15)
[ ] #3: Finish report - Complete Q4 financial analysis for... (Created: 2025-12-24 11:00)
```

---

## Storage: TaskStorage

### Definition

```python
from typing import Optional

class TaskStorage:
    """
    In-memory storage for Task entities.

    Provides CRUD operations with O(1) lookup by ID.
    Designed for easy replacement with persistent storage in Phase II.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

### Interface Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `create` | `(task: Task) -> Task` | Created task | Store new task |
| `read` | `(task_id: int) -> Optional[Task]` | Task or None | Get by ID |
| `read_all` | `() -> list[Task]` | List of tasks | Get all tasks |
| `update` | `(task: Task) -> Optional[Task]` | Updated or None | Update existing |
| `delete` | `(task_id: int) -> bool` | True/False | Remove by ID |
| `next_id` | `() -> int` | New ID | Generate unique ID |

### Storage Internals

```python
# Internal structure
_tasks: dict[int, Task] = {}  # task_id -> Task mapping
_next_id: int = 1              # Auto-increment counter

# ID Generation
def next_id(self) -> int:
    """Generate unique ID (sequential, never reused)."""
    id = self._next_id
    self._next_id += 1
    return id
```

### Storage Behavior

| Operation | Behavior | Time Complexity |
|-----------|----------|-----------------|
| Create | Add to dict, increment counter | O(1) |
| Read | Lookup by key | O(1) |
| Read All | Convert dict values to list | O(n) |
| Update | Replace in dict | O(1) |
| Delete | Remove from dict | O(1) |

---

## Data Flow

### Add Task Flow

```
User Input          Validation           Storage              Response
    │                   │                   │                    │
    │  title, desc      │                   │                    │
    ├──────────────────►│                   │                    │
    │                   │ trim, validate    │                    │
    │                   ├──────────────────►│                    │
    │                   │                   │ next_id()          │
    │                   │                   │ create Task        │
    │                   │                   │ store in _tasks    │
    │                   │◄──────────────────┤                    │
    │                   │                   │ return Task        │
    │◄──────────────────┤                   │                    │
    │  Task object      │                   │                    │
```

### Update Task Flow

```
User Input          Lookup              Validation           Update
    │                   │                   │                   │
    │  task_id          │                   │                   │
    ├──────────────────►│                   │                   │
    │                   │ read(task_id)     │                   │
    │                   │                   │                   │
    │                   │ None = not found  │                   │
    │◄──────────────────┤                   │                   │
    │                   │                   │                   │
    │                   │ Task found        │                   │
    │  new title/desc   │                   │                   │
    ├───────────────────┼──────────────────►│                   │
    │                   │                   │ trim, validate    │
    │                   │                   ├──────────────────►│
    │                   │                   │                   │ update
    │◄──────────────────┼───────────────────┼───────────────────┤
    │  Updated Task     │                   │                   │
```

---

## Serialization (Future Extensibility)

### To Dictionary

```python
from dataclasses import asdict

def task_to_dict(task: Task) -> dict:
    """Convert Task to dictionary for JSON serialization."""
    data = asdict(task)
    data["created_at"] = task.created_at.isoformat()
    return data
```

### From Dictionary

```python
def task_from_dict(data: dict) -> Task:
    """Reconstruct Task from dictionary."""
    data["created_at"] = datetime.fromisoformat(data["created_at"])
    return Task(**data)
```

### JSON Example

```json
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Get milk and bread",
    "is_completed": false,
    "created_at": "2025-12-24T10:30:00"
}
```

---

## Phase II Evolution Path

### Current (Phase I)

```python
class TaskStorage:
    """In-memory dictionary storage."""
    def __init__(self):
        self._tasks: dict[int, Task] = {}
```

### Future (Phase II)

```python
# Option A: JSON File
class JsonTaskStorage:
    """JSON file persistence."""
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._tasks = self._load()

# Option B: SQLite
class SqliteTaskStorage:
    """SQLite database storage."""
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)

# Option C: PostgreSQL (Phase II+)
class PostgresTaskStorage:
    """PostgreSQL via SQLModel."""
    def __init__(self, connection_string: str):
        self._engine = create_engine(connection_string)
```

### Interface Contract

All storage implementations must provide:
- `create(task) -> Task`
- `read(task_id) -> Task | None`
- `read_all() -> list[Task]`
- `update(task) -> Task | None`
- `delete(task_id) -> bool`
- `next_id() -> int`

---

## Constants

```python
# Validation limits
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500

# Display settings
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DESCRIPTION_PREVIEW_LENGTH = 50

# Status indicators
STATUS_INCOMPLETE = "[ ]"
STATUS_COMPLETE = "[x]"
```

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Entity** | Single `Task` dataclass |
| **Storage** | In-memory `dict[int, Task]` |
| **ID Strategy** | Auto-increment, never reused |
| **Lookup** | O(1) by ID |
| **Extensibility** | Interface pattern for Phase II storage swap |
