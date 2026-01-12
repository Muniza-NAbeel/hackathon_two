# Conversation History Loader Skill (T139)

**Pattern for loading conversation history with caching and pagination**

## Overview

The conversation history loader skill provides efficient retrieval of conversation messages from the database with support for caching and pagination to optimize performance and reduce database load.

## Responsibilities

- Load conversation messages from PostgreSQL
- Validate conversation ownership (user_id match)
- Support pagination for long conversations
- Implement caching strategy for frequently accessed conversations
- Handle edge cases (empty conversations, deleted conversations)

## Implementation Pattern

### Basic Loading

```python
from typing import List, Dict, Any
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message

def load_conversation_history(
    conversation_id: int,
    user_id: int,
    db: Session,
    offset: int = 0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Load conversation history with pagination.

    Args:
        conversation_id: Conversation ID to load
        user_id: User ID (for ownership validation)
        db: Database session
        offset: Number of messages to skip (default: 0)
        limit: Maximum messages to return (default: 50)

    Returns:
        List of message dictionaries with role and content

    Raises:
        PermissionError: If conversation doesn't belong to user
        ValueError: If conversation doesn't exist
    """
    # Validate ownership
    conv = db.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conv:
        raise PermissionError("Conversation not found or doesn't belong to user")

    # Load messages with pagination
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(offset)
        .limit(limit)
    ).all()

    # Format for agent consumption
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]
```

### With Caching (Redis)

```python
import json
import redis
from typing import Optional

class ConversationHistoryLoader:
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    def get_cache_key(self, conversation_id: int, offset: int, limit: int) -> str:
        """Generate cache key for conversation history."""
        return f"conv:{conversation_id}:offset:{offset}:limit:{limit}"

    def load_with_cache(
        self,
        conversation_id: int,
        user_id: int,
        db: Session,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Load conversation history with Redis caching."""

        # Try cache first
        if self.redis:
            cache_key = self.get_cache_key(conversation_id, offset, limit)
            cached = self.redis.get(cache_key)

            if cached:
                return json.loads(cached)

        # Load from database
        history = load_conversation_history(
            conversation_id, user_id, db, offset, limit
        )

        # Store in cache
        if self.redis and history:
            cache_key = self.get_cache_key(conversation_id, offset, limit)
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(history)
            )

        return history

    def invalidate_cache(self, conversation_id: int):
        """Invalidate all cache entries for a conversation."""
        if self.redis:
            # Delete all keys matching pattern
            pattern = f"conv:{conversation_id}:*"
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
```

## Usage Examples

### Simple Usage (No Caching)

```python
from app.db.database import get_session
from app.services.conversation_loader import load_conversation_history

# In endpoint
async def get_history(conversation_id: int, user_id: int):
    db = get_session()

    try:
        history = load_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id,
            db=db
        )
        return {"messages": history}

    except PermissionError:
        raise HTTPException(403, "Access denied")
    except ValueError:
        raise HTTPException(404, "Conversation not found")
```

### Paginated Loading

```python
# Load first 50 messages
page_1 = load_conversation_history(
    conversation_id=123,
    user_id=456,
    db=db,
    offset=0,
    limit=50
)

# Load next 50 messages
page_2 = load_conversation_history(
    conversation_id=123,
    user_id=456,
    db=db,
    offset=50,
    limit=50
)
```

### With Caching

```python
from app.services.cache import get_redis_client

loader = ConversationHistoryLoader(redis_client=get_redis_client())

# First call - loads from DB and caches
history = loader.load_with_cache(
    conversation_id=123,
    user_id=456,
    db=db
)

# Subsequent calls within 5 minutes - served from cache
history = loader.load_with_cache(
    conversation_id=123,
    user_id=456,
    db=db
)  # Fast! From Redis

# After adding new message - invalidate cache
loader.invalidate_cache(conversation_id=123)
```

## Performance Considerations

### Database Optimization

```sql
-- Essential index for query performance
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Compound index for better performance
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at);
```

### Pagination Best Practices

- **Default limit**: 50 messages (balances performance and UX)
- **Maximum limit**: 100 messages (prevent excessive memory usage)
- **Offset-based**: Simple but not ideal for very large conversations
- **Cursor-based** (future): Better for infinite scroll

### Caching Strategy

**When to cache:**
- Conversations with > 10 messages
- Frequently accessed conversations
- Recent conversations (last 24 hours)

**When NOT to cache:**
- New conversations (< 5 messages)
- Conversations with recent updates (< 1 minute ago)

**Cache invalidation triggers:**
- New message added
- Message deleted
- Conversation deleted

## Error Handling

```python
def load_conversation_history_safe(
    conversation_id: int,
    user_id: int,
    db: Session,
    offset: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """Load conversation history with comprehensive error handling."""

    try:
        # Validate conversation_id
        if conversation_id <= 0:
            return {
                "error": "Invalid conversation ID",
                "messages": []
            }

        # Load history
        messages = load_conversation_history(
            conversation_id, user_id, db, offset, limit
        )

        return {
            "success": True,
            "messages": messages,
            "total": len(messages),
            "offset": offset,
            "limit": limit
        }

    except PermissionError:
        return {
            "error": "Access denied",
            "messages": []
        }

    except ValueError:
        return {
            "error": "Conversation not found",
            "messages": []
        }

    except Exception as e:
        logger.error(f"Failed to load conversation history: {e}")
        return {
            "error": "Failed to load conversation history",
            "messages": []
        }
```

## Testing

```python
import pytest
from app.models.conversation import Conversation, Message

def test_load_conversation_history(db_session, test_user):
    # Create conversation
    conv = Conversation(user_id=test_user.id)
    db_session.add(conv)
    db_session.commit()

    # Add messages
    msg1 = Message(
        conversation_id=conv.id,
        user_id=test_user.id,
        role="user",
        content="Hello"
    )
    msg2 = Message(
        conversation_id=conv.id,
        user_id=test_user.id,
        role="assistant",
        content="Hi there!"
    )
    db_session.add_all([msg1, msg2])
    db_session.commit()

    # Load history
    history = load_conversation_history(
        conversation_id=conv.id,
        user_id=test_user.id,
        db=db_session
    )

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"

def test_load_conversation_ownership(db_session, test_user):
    # User 1 creates conversation
    conv = Conversation(user_id=test_user.id)
    db_session.add(conv)
    db_session.commit()

    # User 2 tries to access
    with pytest.raises(PermissionError):
        load_conversation_history(
            conversation_id=conv.id,
            user_id=999,  # Different user
            db=db_session
        )
```

## Integration with Agent

```python
from app.services.agent_runner import AgentRunner

class AgentRunner:
    async def run(self, message: str, conversation_id: int, user_id: int):
        # Load conversation history
        history = load_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id,
            db=self.db
        )

        # Pass to AI agent
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + history + [
            {"role": "user", "content": message}
        ]

        # Get AI response
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        return response.choices[0].message.content
```

## Related Documentation

- [Architecture](../docs/architecture.md) - Overall system design
- [API Reference](../docs/api_reference.md) - REST API endpoints
- [Conversation Agent Spec](../agents/conversation_agent.md) - Agent responsibilities

---

**Skill Owner:** Conversation Agent
**Dependencies:** PostgreSQL, SQLModel, Optional: Redis
**Performance Target:** < 50ms database query, < 5ms cache hit
