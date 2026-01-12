# Conversation Agent Specification (T146)

**Primary Responsibility:** Conversation persistence, message storage, and history loading

## Overview

The Conversation Agent manages all conversation and message persistence operations. It provides a clean interface for creating conversations, storing messages, loading conversation history, and managing conversation metadata. This agent owns the conversation database schema and ensures data integrity.

## Responsibilities

### 1. Conversation Persistence
- Create new conversations for users
- Load existing conversations by ID
- List user's conversations (with pagination)
- Update conversation metadata (last_message_at, title)
- Delete conversations (soft delete)
- Enforce user ownership validation

### 2. Message Storage
- Append user messages to conversations
- Append assistant messages to conversations
- Store message metadata (role, content, timestamp)
- Support message retrieval by conversation ID
- Maintain message ordering (chronological)

### 3. History Loading
- Load conversation history with pagination
- Filter messages by conversation ID
- Return messages in chronological order
- Support offset/limit pagination
- Validate conversation ownership before loading

### 4. Database Schema Management
- Define Conversation and Message SQLModel models
- Create and maintain database indexes
- Enforce foreign key constraints
- Handle database migrations

## Inputs

### Create Conversation
```python
{
    "user_id": int,                    # Required
    "title": str | None = None,        # Optional, auto-generated if None
    "metadata": Dict[str, Any] = {},   # Optional custom metadata
}
```

### Add Message
```python
{
    "conversation_id": int,  # Required
    "user_id": int,          # Required (for ownership validation)
    "role": "user" | "assistant" | "system",  # Required
    "content": str,          # Required (1-10000 chars)
    "metadata": Dict[str, Any] = {},  # Optional
}
```

### Load History
```python
{
    "conversation_id": int,  # Required
    "user_id": int,          # Required (for ownership validation)
    "offset": int = 0,       # Optional, default: 0
    "limit": int = 50,       # Optional, default: 50 (max: 100)
}
```

### List Conversations
```python
{
    "user_id": int,      # Required
    "offset": int = 0,   # Optional
    "limit": int = 20,   # Optional (max: 100)
}
```

## Outputs

### Create Conversation (Success)
```python
{
    "id": 123,
    "user_id": 789,
    "title": "Conversation on 2025-12-31",
    "created_at": "2025-12-31T10:30:00Z",
    "last_message_at": None,
    "message_count": 0,
}
```

### Add Message (Success)
```python
{
    "id": 456,
    "conversation_id": 123,
    "user_id": 789,
    "role": "user",
    "content": "Add buy milk to my list",
    "created_at": "2025-12-31T10:30:05Z",
}
```

### Load History (Success)
```python
{
    "conversation_id": 123,
    "messages": [
        {
            "id": 456,
            "role": "user",
            "content": "Add buy milk to my list",
            "created_at": "2025-12-31T10:30:05Z",
        },
        {
            "id": 457,
            "role": "assistant",
            "content": "I've added 'buy milk' to your task list.",
            "created_at": "2025-12-31T10:30:07Z",
        },
    ],
    "total": 2,
    "offset": 0,
    "limit": 50,
}
```

### List Conversations (Success)
```python
{
    "conversations": [
        {
            "id": 123,
            "title": "Task management",
            "last_message_at": "2025-12-31T10:30:07Z",
            "message_count": 2,
            "created_at": "2025-12-31T10:30:00Z",
        },
        # ... more conversations
    ],
    "total": 10,
    "offset": 0,
    "limit": 20,
}
```

## Constraints

### Performance Constraints
- **Database Query Time:** < 50ms per query (p95)
- **Message Storage Time:** < 100ms per message
- **History Loading Time:** < 50ms for 50 messages
- **Concurrent Writes:** Support 100+ concurrent message writes

### Functional Constraints
- **Message Ordering:** Messages always returned in chronological order
- **User Isolation:** Users can only access their own conversations
- **Foreign Key Integrity:** Messages must reference valid conversations
- **Soft Deletes:** Deleted conversations marked as deleted (not removed)

### Data Constraints
- **Message Content Length:** 1-10,000 characters
- **Conversation Title Length:** 1-200 characters
- **Max Messages per Conversation:** No hard limit (pagination required)
- **Max Conversations per User:** No hard limit

## Database Schema

### Conversation Model (SQLModel)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """Conversation model for storing chat conversations."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, default="New Conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None  # Soft delete
    metadata: dict = Field(default={}, sa_column=Column(JSON))

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        indexes = [
            ("user_id", "created_at"),  # For listing conversations
            ("user_id", "last_message_at"),  # For sorting by recent
        ]
```

### Message Model (SQLModel)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Message(SQLModel, table=True):
    """Message model for storing conversation messages."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # user, assistant, system
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    metadata: dict = Field(default={}, sa_column=Column(JSON))

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        indexes = [
            ("conversation_id", "created_at"),  # For loading history
            ("user_id", "created_at"),  # For user's messages
        ]
```

### Database Indexes

```sql
-- Conversations table
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at);
CREATE INDEX idx_conversations_user_last_msg ON conversations(user_id, last_message_at);

-- Messages table
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_user_created ON messages(user_id, created_at);
```

## Architecture

### ConversationService Implementation

```python
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationService:
    """Service for conversation and message persistence."""

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self,
        user_id: int,
        title: str | None = None,
        metadata: Dict[str, Any] = {}
    ) -> Conversation:
        """
        Create a new conversation for user.

        Args:
            user_id: User ID
            title: Conversation title (auto-generated if None)
            metadata: Optional custom metadata

        Returns:
            Created conversation object
        """
        # Auto-generate title if not provided
        if not title:
            title = f"Conversation on {datetime.utcnow().strftime('%Y-%m-%d')}"

        # Create conversation
        conversation = Conversation(
            user_id=user_id,
            title=title,
            metadata=metadata,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get conversation by ID with ownership validation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for ownership validation)

        Returns:
            Conversation object or None if not found/unauthorized

        Raises:
            PermissionError: If conversation doesn't belong to user
        """
        conversation = self.db.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.deleted_at == None  # Exclude soft-deleted
            )
        ).first()

        if not conversation:
            return None

        return conversation

    def add_message(
        self,
        conversation_id: int,
        user_id: int,
        role: str,
        content: str,
        metadata: Dict[str, Any] = {}
    ) -> Message:
        """
        Add message to conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata

        Returns:
            Created message object

        Raises:
            PermissionError: If conversation doesn't belong to user
            ValueError: If conversation not found or role invalid
        """
        # Validate conversation ownership
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise PermissionError("Conversation not found or access denied")

        # Validate role
        if role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {role}")

        # Validate content length
        if not content or len(content) > 10000:
            raise ValueError("Content must be 1-10000 characters")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata=metadata,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # Update conversation last_message_at
        self.update_last_message_time(conversation_id)

        return message

    def load_history(
        self,
        conversation_id: int,
        user_id: int,
        offset: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Load conversation history with pagination.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for ownership validation)
            offset: Number of messages to skip
            limit: Maximum messages to return (max: 100)

        Returns:
            Dictionary with messages and pagination info

        Raises:
            PermissionError: If conversation doesn't belong to user
        """
        # Validate ownership
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise PermissionError("Conversation not found or access denied")

        # Enforce max limit
        limit = min(limit, 100)

        # Load messages
        messages = self.db.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
        ).all()

        # Get total count
        total = self.db.exec(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        ).one()

        # Format messages
        formatted_messages = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

        return {
            "conversation_id": conversation_id,
            "messages": formatted_messages,
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    def update_last_message_time(self, conversation_id: int):
        """Update conversation's last_message_at timestamp."""
        conversation = self.db.get(Conversation, conversation_id)
        if conversation:
            conversation.last_message_at = datetime.utcnow()
            self.db.add(conversation)
            self.db.commit()

    def list_conversations(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        List user's conversations with pagination.

        Args:
            user_id: User ID
            offset: Number of conversations to skip
            limit: Maximum conversations to return (max: 100)

        Returns:
            Dictionary with conversations and pagination info
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Load conversations (ordered by most recent)
        conversations = self.db.exec(
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at == None
            )
            .order_by(Conversation.last_message_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        # Get total count
        total = self.db.exec(
            select(func.count(Conversation.id))
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at == None
            )
        ).one()

        # Format conversations
        formatted_conversations = [
            {
                "id": conv.id,
                "title": conv.title,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": len(conv.messages),
                "created_at": conv.created_at.isoformat(),
            }
            for conv in conversations
        ]

        return {
            "conversations": formatted_conversations,
            "total": total,
            "offset": offset,
            "limit": limit,
        }
```

## Error Handling

### Validation Errors
- **Invalid Role:** role not in ["user", "assistant", "system"]
- **Empty Content:** content is empty or None
- **Content Too Long:** content exceeds 10,000 characters
- **Invalid Pagination:** offset < 0 or limit > 100

### Permission Errors
- **Conversation Not Found:** conversation_id doesn't exist
- **Access Denied:** conversation belongs to different user
- **Soft Deleted:** conversation was deleted

### Database Errors
- **Foreign Key Violation:** conversation_id doesn't exist
- **Unique Constraint Violation:** Unlikely, but handle gracefully
- **Connection Error:** Database unavailable

## Testing Strategy

### Unit Tests
- Create conversation (valid inputs)
- Create conversation (auto-generated title)
- Add message (valid role and content)
- Add message (invalid role → ValueError)
- Load history (valid conversation)
- Load history (unauthorized → PermissionError)
- Pagination (offset/limit boundaries)

### Integration Tests
- End-to-end conversation creation → message addition → history loading
- Concurrent message writes to same conversation
- Soft delete conversation → cannot load
- Foreign key constraint enforcement

### Acceptance Tests
- User creates conversation → conversation ID returned
- User adds message → message persisted with correct timestamp
- User loads history → messages in chronological order
- User lists conversations → sorted by most recent

## Metrics and Monitoring

### Key Metrics
- **Conversation Creation Rate:** Conversations per minute
- **Message Creation Rate:** Messages per second
- **Database Query Time:** p50, p95, p99 latency
- **History Load Time:** Time to load 50 messages
- **Storage Growth:** Database size growth rate

### Alerts
- Database query time > 100ms (p95)
- Message creation failures > 1%
- Database connection pool exhausted

## Related Documentation

- [Conversation History Loader Skill](../skills/conversation_history_loader.md) - Loading patterns
- [Chat API Agent](./chat_api_agent.md) - API orchestration
- [AI Agent](./ai_agent.md) - Message consumption
- [Database Schema](../docs/database_schema.md) - Full schema
- [Architecture](../docs/architecture.md) - System design

---

**Agent Owner:** Backend Team
**Dependencies:** SQLModel, Neon PostgreSQL
**Security Level:** High (user data persistence)
**Deployment:** Service layer (called by API endpoints)
**Performance Target:** < 50ms database queries, < 100ms message writes
**Data Integrity:** Foreign key constraints, soft deletes, chronological ordering
