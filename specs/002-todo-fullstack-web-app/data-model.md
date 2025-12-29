# Data Model: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web-app`
**Date**: 2025-12-25
**ORM**: SQLModel
**Database**: Neon Serverless PostgreSQL

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                                │
│  (Managed by Better Auth - reference only)                  │
├─────────────────────────────────────────────────────────────┤
│  id          : UUID [PK]                                    │
│  email       : VARCHAR(255) [UNIQUE, NOT NULL]              │
│  name        : VARCHAR(255) [NULL]                          │
│  created_at  : TIMESTAMP [NOT NULL, DEFAULT NOW()]          │
│  updated_at  : TIMESTAMP [NOT NULL, DEFAULT NOW()]          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         TASKS                                │
├─────────────────────────────────────────────────────────────┤
│  id          : UUID [PK]                                    │
│  user_id     : UUID [FK → users.id, NOT NULL]               │
│  title       : VARCHAR(200) [NOT NULL]                      │
│  description : TEXT [NULL]                                  │
│  completed   : BOOLEAN [NOT NULL, DEFAULT FALSE]            │
│  due_date    : TIMESTAMP [NULL]                             │
│  created_at  : TIMESTAMP [NOT NULL, DEFAULT NOW()]          │
│  updated_at  : TIMESTAMP [NOT NULL, DEFAULT NOW()]          │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### User Entity (Reference - Managed by Better Auth)

Better Auth manages the users table. We reference it but do not define it.

**Purpose**: Represents an authenticated person using the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| `name` | VARCHAR(255) | NULLABLE | Display name |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

**Relationships**:
- Has many Tasks (1:N)

---

### Task Entity

**Purpose**: Represents a work item belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY, NOT NULL | Owner reference |
| `title` | VARCHAR(200) | NOT NULL | Task title (1-200 chars) |
| `description` | TEXT | NULLABLE | Optional description (max 1000 chars) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `due_date` | TIMESTAMP | NULLABLE | Optional due date |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Relationships**:
- Belongs to one User (N:1)

**Indexes**:
| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_tasks_user_id` | `user_id` | Filter tasks by owner |
| `idx_tasks_completed` | `completed` | Filter by completion status |
| `idx_tasks_user_completed` | `user_id, completed` | Combined filter |
| `idx_tasks_created_at` | `created_at` | Sort by creation date |
| `idx_tasks_due_date` | `due_date` | Sort by due date |

---

## SQLModel Definitions

### Task Model

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    """Base task fields shared across create/update/read."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    """Fields required to create a task."""
    pass

class TaskUpdate(SQLModel):
    """Fields allowed to update (all optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[datetime] = None

class Task(TaskBase, table=True):
    """Database model for tasks table."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskRead(TaskBase):
    """Task response schema."""
    id: UUID
    user_id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
```

---

## Validation Rules

### Title Validation
- **Required**: Cannot be null or empty
- **Length**: 1-200 characters
- **Sanitization**: Strip leading/trailing whitespace
- **Error**: "Title is required and must be 1-200 characters"

### Description Validation
- **Optional**: Can be null
- **Length**: 0-1000 characters when provided
- **Sanitization**: Strip leading/trailing whitespace
- **Error**: "Description must not exceed 1000 characters"

### Due Date Validation
- **Optional**: Can be null
- **Format**: ISO 8601 datetime
- **Constraint**: No past date validation (users can set any date)
- **Error**: "Invalid date format"

### User ID Validation
- **Required**: Must match authenticated user
- **Foreign Key**: Must reference existing user
- **Error**: "Invalid user reference"

---

## State Transitions

### Task Completion State

```
┌──────────────┐     toggle      ┌──────────────┐
│   PENDING    │ ◄─────────────► │  COMPLETED   │
│ completed=F  │                 │ completed=T  │
└──────────────┘                 └──────────────┘
```

**Transition Rules**:
- Any task can be toggled between pending and completed
- Transition updates `updated_at` timestamp
- No intermediate states

### Task Lifecycle

```
     CREATE                UPDATE                 DELETE
        │                    │                      │
        ▼                    ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   ACTIVE    │ ───► │  MODIFIED   │ ───► │  DELETED    │
└─────────────┘      └─────────────┘      └─────────────┘
                           │
                           ▼
                    (updates timestamp)
```

**Lifecycle Rules**:
- Tasks are soft-created (immediately active)
- Updates are immediate (no draft state)
- Deletes are hard deletes (no soft delete)

---

## Database Migrations

### Initial Migration (001_create_tasks_table)

```sql
-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Query Patterns

### List Tasks with Filtering and Sorting

```python
# Filter by status
def get_tasks(
    user_id: UUID,
    status: Optional[str] = None,  # "pending", "completed", "all"
    sort_by: str = "created_at",   # "title", "created_at", "due_date"
    sort_order: str = "desc",      # "asc", "desc"
    page: int = 1,
    per_page: int = 50
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply sorting
    sort_column = getattr(Task, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Handle null due_dates (appear last when sorting by due_date)
    if sort_by == "due_date":
        query = query.order_by(Task.due_date.is_(None), sort_column)

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    return session.exec(query).all()
```

### Ownership Enforcement

```python
def get_task_with_ownership_check(
    task_id: UUID,
    user_id: UUID
) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return task
```

---

## Data Integrity Constraints

| Constraint | Type | Description |
|------------|------|-------------|
| `tasks_pkey` | PRIMARY KEY | Unique task identifier |
| `tasks_user_id_fkey` | FOREIGN KEY | References users.id |
| `tasks_title_check` | CHECK | title length 1-200 |
| `tasks_description_check` | CHECK | description length ≤ 1000 |
| ON DELETE CASCADE | REFERENTIAL | Delete tasks when user deleted |
