"""
Message model for Phase 3 AI Chatbot

Represents individual messages within a conversation.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID as PyUUID
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Each message belongs to a conversation and has a role (user or assistant).
    Messages store the chat history for context and replay.

    Fields:
        id: Primary key
        conversation_id: Foreign key to conversation
        user_id: Foreign key to user (UUID from Phase 2 auth)
        role: Message role (user, assistant, system)
        content: Message text content
        tool_calls: Optional JSON array of tool calls made by assistant
        tool_results: Optional JSON array of tool results
        created_at: Timestamp of message creation
    """
    __tablename__ = "messages"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: PyUUID = Field(foreign_key="users.id", index=True, sa_type=UUID(as_uuid=True))

    # Message Details
    role: str = Field(max_length=50)  # user, assistant, system
    content: str = Field(sa_column=Column(Text))  # Use Text for long content

    # Tool Execution (for assistant messages)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_results: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (not in database, only for ORM)
    # conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "role": "user",
                "content": "Create a task to buy groceries",
            }
        }
