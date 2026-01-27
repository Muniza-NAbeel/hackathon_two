# Phase 5 Data Model

**Date**: 2026-01-18
**Feature**: 005-Advanced-Cloud-Deployment
**Status**: Complete

## Overview

This document defines the data models for Phase 5 event-driven architecture. It extends the existing Phase 3 Task model and adds new models for events and service state.

---

## 1. Existing Models (READ-ONLY - Phase 3)

### Task Model (Extended)

The existing Task model from Phase 3 already includes fields needed for Phase 5:

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Task Details
    title: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=2000)

    # Status
    status: str = Field(default="pending")  # pending, in_progress, completed
    completed: bool = Field(default=False)

    # Advanced Features (Phase 1)
    priority: str = Field(default="medium")  # low, medium, high, urgent
    tags: Optional[List[str]] = Field(sa_column=Column(JSON))
    recurrence: str = Field(default="none")  # none, daily, weekly, monthly
    notes: Optional[List[dict]] = Field(sa_column=Column(JSON))

    # Dates
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### New Fields Required for Phase 5

Add to Task model via migration:

```python
# Reminder Fields
remind_at: Optional[datetime] = Field(default=None)  # When to send reminder
reminder_sent: bool = Field(default=False)  # Prevent duplicate reminders
```

---

## 2. Event Models (New)

### TaskEvent

CloudEvents-formatted event for task lifecycle changes.

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

class TaskEventData(BaseModel):
    """Task data embedded in event"""
    id: int
    user_id: UUID
    title: str
    description: Optional[str] = None
    status: str
    completed: bool
    priority: str
    tags: Optional[list[str]] = None
    recurrence: str
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class TaskEventMetadata(BaseModel):
    """Event metadata"""
    source: str = "chat-backend"
    version: str = "1.0"

class TaskEvent(BaseModel):
    """CloudEvents-formatted task event"""
    # CloudEvents required fields
    specversion: str = "1.0"
    type: Literal[
        "com.todo.task.created",
        "com.todo.task.updated",
        "com.todo.task.completed",
        "com.todo.task.deleted"
    ]
    source: str = "/services/chat-backend"
    id: UUID  # event_id for idempotency
    time: datetime
    datacontenttype: str = "application/json"

    # Custom data
    data: TaskEventData

    # Extensions
    userid: UUID  # For routing/filtering
    taskid: int

class Config:
    json_schema_extra = {
        "example": {
            "specversion": "1.0",
            "type": "com.todo.task.completed",
            "source": "/services/chat-backend",
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "time": "2026-01-18T10:00:00Z",
            "datacontenttype": "application/json",
            "userid": "123e4567-e89b-12d3-a456-426614174000",
            "taskid": 42,
            "data": {
                "id": 42,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Morning standup",
                "status": "completed",
                "completed": True,
                "priority": "high",
                "recurrence": "daily",
                "due_date": "2026-01-18T09:00:00Z",
                "created_at": "2026-01-15T10:00:00Z",
                "updated_at": "2026-01-18T10:00:00Z"
            }
        }
    }
```

### ReminderEvent

Event for triggering notifications.

```python
class ReminderEvent(BaseModel):
    """CloudEvents-formatted reminder event"""
    # CloudEvents required fields
    specversion: str = "1.0"
    type: str = "com.todo.reminder.due"
    source: str = "/services/chat-backend"
    id: UUID  # event_id for idempotency
    time: datetime
    datacontenttype: str = "application/json"

    # Custom data
    data: ReminderEventData

    # Extensions
    userid: UUID
    taskid: int

class ReminderEventData(BaseModel):
    """Reminder data"""
    task_id: int
    user_id: UUID
    title: str
    description: Optional[str] = None
    due_at: datetime
    remind_at: datetime
    reminder_type: Literal["before_due", "overdue"] = "before_due"
```

---

## 3. Service State Models

### ProcessedEvent (Idempotency Tracking)

Stored in Dapr State Store for deduplication.

```python
class ProcessedEvent(BaseModel):
    """Record of processed event for idempotency"""
    event_id: UUID
    event_type: str
    processed_at: datetime
    service: str  # notification-service, recurring-task-service
    result: str  # success, skipped, error

    class Config:
        # TTL: 24 hours (86400 seconds)
        pass
```

### State Store Key Pattern

```
{service}:processed:{event_id}
```

Examples:
- `notification-service:processed:550e8400-e29b-41d4-a716-446655440000`
- `recurring-task-service:processed:550e8400-e29b-41d4-a716-446655440001`

---

## 4. API Request/Response Models

### Internal Task Creation (Service-to-Service)

Used by Recurring Task Service to create tasks via Dapr Service Invocation.

```python
class InternalTaskCreate(BaseModel):
    """Request to create task from internal service"""
    user_id: UUID
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    tags: Optional[list[str]] = None
    recurrence: str = "none"
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    source_task_id: Optional[int] = None  # Original recurring task

class InternalTaskResponse(BaseModel):
    """Response from internal task creation"""
    id: int
    user_id: UUID
    title: str
    status: str
    created_at: datetime
```

### Reminder Check Response

Response from `/reminder-cron` endpoint.

```python
class ReminderCheckResponse(BaseModel):
    """Response from reminder check endpoint"""
    processed: int  # Number of reminders sent
    errors: int  # Number of failures
    next_check: datetime  # Expected next cron trigger
```

---

## 5. Database Migrations

### Migration: Add Reminder Fields to Tasks

```python
"""Add reminder fields to tasks table

Revision ID: phase5_001_reminder_fields
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean(), default=False))
    op.create_index('ix_tasks_remind_at', 'tasks', ['remind_at'],
                    postgresql_where=sa.text('reminder_sent = false'))

def downgrade():
    op.drop_index('ix_tasks_remind_at', 'tasks')
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'remind_at')
```

### Migration: Add Dapr State Table (for PostgreSQL state store)

```python
"""Create Dapr state table

Revision ID: phase5_002_dapr_state
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'dapr_state',
        sa.Column('key', sa.String(255), primary_key=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('insert_date', sa.DateTime(), default=sa.func.now()),
        sa.Column('update_date', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('expiration_time', sa.DateTime(), nullable=True)
    )
    op.create_index('ix_dapr_state_expiration', 'dapr_state', ['expiration_time'])

def downgrade():
    op.drop_table('dapr_state')
```

---

## 6. Entity Relationships

```
┌─────────────┐         ┌─────────────────┐
│    User     │ 1────n  │      Task       │
├─────────────┤         ├─────────────────┤
│ id (UUID)   │         │ id (int)        │
│ email       │         │ user_id (FK)    │
│ ...         │         │ title           │
└─────────────┘         │ recurrence      │
                        │ remind_at       │
                        │ reminder_sent   │
                        └─────────────────┘
                                │
                                │ triggers
                                ▼
                        ┌─────────────────┐
                        │   TaskEvent     │
                        ├─────────────────┤
                        │ id (UUID)       │
                        │ type            │
                        │ task_id         │
                        │ user_id         │
                        │ data (JSON)     │
                        └─────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │ ReminderEvent │       │ ProcessedEvent│
            ├───────────────┤       ├───────────────┤
            │ (Kafka topic) │       │ (State Store) │
            │ reminders     │       │ idempotency   │
            └───────────────┘       └───────────────┘
```

---

## 7. Validation Rules

### Task Validation (Extended)

| Field | Rule | Error Message |
|-------|------|---------------|
| remind_at | Must be before due_date if both set | "Reminder must be before due date" |
| remind_at | Must be in future when setting | "Reminder time must be in future" |
| recurrence | One of: none, daily, weekly, monthly | "Invalid recurrence pattern" |

### Event Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| id | Valid UUID v4 | "Invalid event ID format" |
| time | ISO 8601 format | "Invalid timestamp format" |
| type | Must be known event type | "Unknown event type" |
| data.user_id | Must match userid extension | "User ID mismatch" |

---

## 8. State Transitions

### Task Status Transitions

```
┌─────────┐     create      ┌─────────────┐
│  (new)  │ ───────────────▶│   pending   │
└─────────┘                 └─────────────┘
                                  │
                          start   │
                                  ▼
                            ┌─────────────┐
                            │ in_progress │
                            └─────────────┘
                                  │
                        complete  │
                                  ▼
                            ┌─────────────┐
┌─────────────┐             │  completed  │───▶ (if recurring)
│ (next task) │◀────────────└─────────────┘     create new task
└─────────────┘    recurring
                   service
```

### Event Processing States

```
Event Received
      │
      ▼
┌─────────────┐
│ Check       │──── already processed ────▶ SKIP
│ Idempotency │
└─────────────┘
      │
      │ not processed
      ▼
┌─────────────┐
│ Process     │──── success ────▶ Mark Processed
│ Event       │
└─────────────┘
      │
      │ failure
      ▼
┌─────────────┐
│ Retry (3x)  │──── all failed ────▶ DLQ
└─────────────┘
```

---

## Summary

| Model | Location | Purpose |
|-------|----------|---------|
| Task (extended) | PostgreSQL | Add remind_at, reminder_sent |
| TaskEvent | Kafka topic | Task lifecycle events |
| ReminderEvent | Kafka topic | Notification triggers |
| ProcessedEvent | Dapr State | Idempotency tracking |
| InternalTaskCreate | API Request | Service-to-service task creation |
