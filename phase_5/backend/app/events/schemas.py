"""
CloudEvents v1.0 Schemas for Phase 5 Event-Driven Architecture

Defines event schemas for task lifecycle and reminder notifications.
All events follow the CloudEvents specification: https://cloudevents.io/
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class TaskEventType(str, Enum):
    """Task lifecycle event types"""
    CREATED = "com.todo.task.created"
    UPDATED = "com.todo.task.updated"
    COMPLETED = "com.todo.task.completed"
    DELETED = "com.todo.task.deleted"


class ReminderEventType(str, Enum):
    """Reminder event types"""
    DUE = "com.todo.reminder.due"


class CloudEventBase(BaseModel):
    """
    CloudEvents v1.0 Base Schema

    Required fields per CloudEvents spec:
    - specversion: Version of CloudEvents spec
    - type: Event type identifier
    - source: Event source identifier
    - id: Unique event ID for idempotency
    """
    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    id: UUID = Field(default_factory=uuid4, description="Unique event ID")
    time: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    datacontenttype: str = Field(default="application/json", description="Content type of data")


class TaskEventData(BaseModel):
    """Task data embedded in event payload"""
    id: int = Field(..., description="Task ID")
    user_id: UUID = Field(..., description="User ID who owns the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: str = Field(..., description="Task status: pending, in_progress, completed")
    completed: bool = Field(..., description="Whether task is completed")
    priority: str = Field(..., description="Task priority: low, medium, high, urgent")
    tags: Optional[List[str]] = Field(default=None, description="Task tags/categories")
    recurrence: str = Field(..., description="Recurrence pattern: none, daily, weekly, monthly")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    remind_at: Optional[datetime] = Field(default=None, description="Reminder time")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

    class Config:
        from_attributes = True


class TaskEvent(CloudEventBase):
    """
    CloudEvents-formatted task lifecycle event

    Published on task CRUD operations:
    - com.todo.task.created: New task created
    - com.todo.task.updated: Task modified
    - com.todo.task.completed: Task marked complete
    - com.todo.task.deleted: Task removed
    """
    type: Literal[
        "com.todo.task.created",
        "com.todo.task.updated",
        "com.todo.task.completed",
        "com.todo.task.deleted"
    ] = Field(..., description="Event type")
    source: str = Field(default="/services/chat-backend", description="Event source")

    # Event payload
    data: TaskEventData = Field(..., description="Task data")

    # CloudEvents extensions for routing
    userid: UUID = Field(..., description="User ID for routing/filtering")
    taskid: int = Field(..., description="Task ID for correlation")

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


class ReminderEventData(BaseModel):
    """Reminder data embedded in event payload"""
    task_id: int = Field(..., description="Task ID")
    user_id: UUID = Field(..., description="User ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    due_at: Optional[datetime] = Field(default=None, description="Task due date")
    remind_at: datetime = Field(..., description="Scheduled reminder time")
    reminder_type: Literal["before_due", "overdue"] = Field(
        default="before_due",
        description="Type of reminder"
    )


class ReminderEvent(CloudEventBase):
    """
    CloudEvents-formatted reminder event

    Published when a task reminder is due:
    - com.todo.reminder.due: Reminder triggered
    """
    type: str = Field(default="com.todo.reminder.due", description="Event type")
    source: str = Field(default="/services/chat-backend", description="Event source")

    # Event payload
    data: ReminderEventData = Field(..., description="Reminder data")

    # CloudEvents extensions for routing
    userid: UUID = Field(..., description="User ID for routing")
    taskid: int = Field(..., description="Task ID for correlation")

    class Config:
        json_schema_extra = {
            "example": {
                "specversion": "1.0",
                "type": "com.todo.reminder.due",
                "source": "/services/chat-backend",
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "time": "2026-01-18T08:55:00Z",
                "datacontenttype": "application/json",
                "userid": "123e4567-e89b-12d3-a456-426614174000",
                "taskid": 42,
                "data": {
                    "task_id": 42,
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Morning standup",
                    "description": "Daily team sync",
                    "due_at": "2026-01-18T09:00:00Z",
                    "remind_at": "2026-01-18T08:55:00Z",
                    "reminder_type": "before_due"
                }
            }
        }
