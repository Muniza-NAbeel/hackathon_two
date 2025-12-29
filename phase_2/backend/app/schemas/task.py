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
    COMPLETED = "completed"


class TaskSortBy(str, Enum):
    """Sort field options for task list."""

    TITLE = "title"
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"


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
        max_length=1000,
        description="Optional task description (max 1000 characters)",
        examples=["Milk, eggs, bread"],
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date",
        examples=["2025-12-31T23:59:59Z"],
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
        max_length=1000,
        description="Updated task description",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Updated due date",
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
                }
            ]
        }
    }


class TaskRead(BaseModel):
    """Response schema for task data."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime]
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
