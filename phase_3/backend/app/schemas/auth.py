"""Authentication response schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""

    user: UserRead
    token: str = Field(description="JWT access token")
    expires_at: datetime = Field(description="Token expiration timestamp")


class ErrorCode(str, Enum):
    """Standardized error codes."""

    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(description="Human-readable error message")
    code: str = Field(description="Machine-readable error code")
    field: Optional[str] = Field(
        default=None,
        description="Field that caused the error (if applicable)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Task not found",
                    "code": "NOT_FOUND",
                    "field": None,
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
