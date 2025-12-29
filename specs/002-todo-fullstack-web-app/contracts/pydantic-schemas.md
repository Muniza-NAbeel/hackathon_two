# Pydantic Schemas: Todo Full-Stack Web Application

**Feature Branch**: `002-todo-fullstack-web-app`
**Date**: 2025-12-25

---

## Overview

This document defines the Pydantic models used for request/response validation in the FastAPI backend. These schemas complement the SQLModel database models defined in `data-model.md`.

---

## Authentication Schemas

### UserRegister

```python
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """Request schema for user registration."""
    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepassword123"]
    )
    name: str | None = Field(
        default=None,
        max_length=255,
        description="Optional display name",
        examples=["John Doe"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securepassword123",
                    "name": "John Doe"
                }
            ]
        }
    }
```

### UserLogin

```python
class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(
        description="Registered email address"
    )
    password: str = Field(
        description="Account password"
    )
```

### UserRead

```python
from datetime import datetime
from uuid import UUID

class UserRead(BaseModel):
    """Response schema for user data."""
    id: UUID
    email: EmailStr
    name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### AuthResponse

```python
class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""
    user: UserRead
    token: str = Field(description="JWT access token")
    expires_at: datetime = Field(description="Token expiration timestamp")
```

---

## Task Schemas

### TaskCreate

```python
class TaskCreate(BaseModel):
    """Request schema for creating a task."""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
        examples=["Buy groceries"]
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional task description (max 1000 characters)",
        examples=["Milk, eggs, bread"]
    )
    due_date: datetime | None = Field(
        default=None,
        description="Optional due date",
        examples=["2025-12-31T23:59:59Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "due_date": "2025-12-31T23:59:59Z"
                }
            ]
        }
    }
```

### TaskUpdate

```python
class TaskUpdate(BaseModel):
    """Request schema for updating a task. All fields optional."""
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated task title"
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Updated task description"
    )
    due_date: datetime | None = Field(
        default=None,
        description="Updated due date"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries today",
                    "description": "Milk, eggs, bread, butter"
                }
            ]
        }
    }
```

### TaskRead

```python
class TaskRead(BaseModel):
    """Response schema for task data."""
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    completed: bool
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### TaskListResponse

```python
class TaskListResponse(BaseModel):
    """Response schema for paginated task list."""
    tasks: list[TaskRead]
    total_count: int = Field(description="Total number of tasks matching filters")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
```

---

## Query Parameter Schemas

### TaskListParams

```python
from enum import Enum
from fastapi import Query

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

class TaskListParams(BaseModel):
    """Query parameters for listing tasks."""
    status: TaskStatus = Field(
        default=TaskStatus.ALL,
        description="Filter by completion status"
    )
    sort_by: TaskSortBy = Field(
        default=TaskSortBy.CREATED_AT,
        description="Sort field"
    )
    sort_order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Sort direction"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number"
    )
    per_page: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Items per page (max 100)"
    )
```

---

## Error Schemas

### ErrorResponse

```python
class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str = Field(description="Human-readable error message")
    code: str = Field(description="Machine-readable error code")
    field: str | None = Field(
        default=None,
        description="Field that caused the error (if applicable)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Task not found",
                    "code": "NOT_FOUND",
                    "field": None
                }
            ]
        }
    }
```

### Error Codes Enum

```python
class ErrorCode(str, Enum):
    """Standardized error codes."""
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

---

## Validation Examples

### Title Validation

```python
# Valid
TaskCreate(title="Buy groceries")  # OK
TaskCreate(title="A")  # OK (min 1 char)
TaskCreate(title="A" * 200)  # OK (max 200 chars)

# Invalid
TaskCreate(title="")  # ValidationError: min_length=1
TaskCreate(title="A" * 201)  # ValidationError: max_length=200
TaskCreate(title=None)  # ValidationError: required field
```

### Description Validation

```python
# Valid
TaskCreate(title="Task", description=None)  # OK
TaskCreate(title="Task", description="")  # OK
TaskCreate(title="Task", description="A" * 1000)  # OK (max 1000)

# Invalid
TaskCreate(title="Task", description="A" * 1001)  # ValidationError: max_length=1000
```

### Email Validation

```python
# Valid
UserRegister(email="user@example.com", password="12345678")  # OK
UserRegister(email="user+tag@sub.domain.com", password="12345678")  # OK

# Invalid
UserRegister(email="invalid", password="12345678")  # ValidationError: invalid email
UserRegister(email="@example.com", password="12345678")  # ValidationError
```

### Password Validation

```python
# Valid
UserRegister(email="user@example.com", password="12345678")  # OK (min 8)
UserRegister(email="user@example.com", password="a" * 100)  # OK

# Invalid
UserRegister(email="user@example.com", password="1234567")  # ValidationError: min_length=8
UserRegister(email="user@example.com", password="")  # ValidationError
```

---

## FastAPI Integration Example

```python
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["Tasks"])

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task: TaskCreate,
    current_user: UserRead = Depends(get_current_user)
):
    """Create a new task for the authenticated user."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(
                detail="You can only create tasks for yourself",
                code=ErrorCode.FORBIDDEN
            ).model_dump()
        )
    # ... create task logic
    return created_task

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID,
    params: TaskListParams = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    """List tasks for the authenticated user with filtering and pagination."""
    # ... list tasks logic
    return TaskListResponse(
        tasks=tasks,
        total_count=total,
        page=params.page,
        per_page=params.per_page,
        total_pages=total_pages
    )
```
