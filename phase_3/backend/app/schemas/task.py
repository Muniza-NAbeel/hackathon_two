"""Task Pydantic schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Filter options for task completion status."""

    ALL = "all"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskSortBy(str, Enum):
    """Sort field options for task list."""

    TITLE = "title"
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"


class SortOrder(str, Enum):
    """Sort direction options."""

    ASC = "asc"
    DESC = "desc"


class TaskCreate(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
        examples=["Buy groceries"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description (max 2000 characters)",
        examples=["Milk, eggs, bread"],
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date",
        examples=["2025-12-31T23:59:59Z"],
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority (low, medium, high, urgent)",
        examples=["high"],
    )
    status: Optional[str] = Field(
        default="pending",
        description="Task status (pending, in_progress, completed)",
        examples=["pending"],
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Optional task tags",
        examples=[["work", "home"]],
    )
    recurrence: Optional[str] = Field(
        default="none",
        description="Recurrence pattern (none, daily, weekly, monthly)",
        examples=["weekly"],
    )

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Strip whitespace and validate title is not empty."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "due_date": "2025-12-31T23:59:59Z",
                    "priority": "high",
                    "tags": ["home", "shopping"],
                    "recurrence": "weekly",
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    """Request schema for updating a task. All fields optional."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated task title",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated task description",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Updated due date",
    )
    priority: Optional[str] = Field(
        default=None,
        description="Updated priority (low, medium, high, urgent)",
    )
    status: Optional[str] = Field(
        default=None,
        description="Updated status (pending, in_progress, completed)",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Updated tags",
    )
    recurrence: Optional[str] = Field(
        default=None,
        description="Updated recurrence (none, daily, weekly, monthly)",
    )

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and validate title is not empty."""
        if v is not None and isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries today",
                    "description": "Milk, eggs, bread, butter",
                    "priority": "high",
                    "tags": ["home", "urgent"],
                }
            ]
        }
    }


class TaskRead(BaseModel):
    """Response schema for task data."""

    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    completed: bool
    due_date: Optional[datetime]
    tags: Optional[list[str]]
    recurrence: str
    notes: Optional[list[dict]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Response schema for paginated task list."""

    tasks: list[TaskRead]
    total_count: int = Field(description="Total number of tasks matching filters")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
