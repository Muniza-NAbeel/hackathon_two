"""
User model for Phase 3 AI Chatbot

Minimal User model for testing purposes to satisfy foreign key constraints.
In production, this references Phase 2's user table.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID as PyUUID, uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model with authentication support.

    Fields:
        id: Primary key (UUID)
        email: User email (unique)
        hashed_password: Bcrypt hashed password
        name: Optional display name
        created_at: Account creation timestamp
    """
    __tablename__ = "users"

    id: Optional[PyUUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_type=UUID(as_uuid=True)
    )
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
