"""
Conversation model for Phase 3 AI Chatbot

Represents a chat conversation session between user and AI agent.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID as PyUUID
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session.

    Each conversation belongs to a single user and contains multiple messages.
    Conversations are persisted to support chat history and context.

    Fields:
        id: Primary key
        user_id: Foreign key to user (UUID from Phase 2 auth)
        title: Optional conversation title (auto-generated or user-set)
        created_at: Timestamp of conversation start
        updated_at: Timestamp of last message
        is_active: Whether conversation is currently active
    """
    __tablename__ = "conversations"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: PyUUID = Field(foreign_key="users.id", index=True, sa_type=UUID(as_uuid=True))

    # Conversation Details
    title: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (not in database, only for ORM)
    # messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Task Management Chat",
                "is_active": True,
            }
        }
