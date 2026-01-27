"""
Task model for Phase 3 AI Chatbot with Advanced Features

Represents a task/todo item that can be created and managed via the AI chatbot.
Includes advanced features from Phase 1: priority, tags, due dates, recurrence, and notes.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID as PyUUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Fields:
        id: Primary key
        user_id: Foreign key to user (UUID from Phase 2 auth)
        title: Task title (required)
        description: Optional detailed description
        status: Task status (pending, in_progress, completed)
        priority: Task priority (low, medium, high)
        due_date: Optional due date
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: PyUUID = Field(foreign_key="users.id", index=True, sa_type=UUID(as_uuid=True))

    # Task Details
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

    # Task Metadata
    status: str = Field(default="pending", max_length=50)  # pending, in_progress, completed
    priority: str = Field(default="medium", max_length=50)  # low, medium, high, urgent
    completed: bool = Field(default=False)  # For compatibility with basic complete/incomplete

    # Advanced Features (from Phase 1)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # Categories: Work, Home, Personal, Shopping, etc.
    recurrence: str = Field(default="none", max_length=50)  # none, daily, weekly, monthly
    notes: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))  # Array of {text, timestamp} objects

    # Dates
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase 5: Reminder Fields
    remind_at: Optional[datetime] = Field(default=None)  # When to send reminder
    reminder_sent: bool = Field(default=False)  # Prevent duplicate reminders

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "priority": "high",
                "due_date": "2025-12-31T10:00:00",
            }
        }
