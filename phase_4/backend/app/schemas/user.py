"""User Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=72,
        description="Password (minimum 8 characters, maximum 72 characters)",
        examples=["securepassword123"],
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional display name",
        examples=["John Doe"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securepassword123",
                    "name": "John Doe",
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(description="Registered email address")
    password: str = Field(description="Account password")


class UserRead(BaseModel):
    """Response schema for user data."""

    id: UUID
    email: EmailStr
    name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
