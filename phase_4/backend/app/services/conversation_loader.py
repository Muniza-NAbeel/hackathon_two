"""
Conversation service for managing chat conversations and message persistence.

This service provides functions to:
- Create new conversations
- Save messages to conversations
- Load conversation history
- Validate conversation ownership

All operations enforce user ownership and maintain chronological message order.
"""

from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.conversation import Conversation
from app.models.message import Message


async def create_conversation(user_id: UUID, db: AsyncSession) -> int:
    """
    Create a new conversation for a user.

    Args:
        user_id: UUID of the user creating the conversation
        db: Database session

    Returns:
        int: ID of the newly created conversation

    Raises:
        ValueError: If user_id is empty or invalid
    """
    # Validate input
    if not user_id:
        raise ValueError("user_id cannot be empty")

    # Create conversation
    conversation = Conversation(
        user_id=user_id,
        is_active=True,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation.id


async def save_message(
    conversation_id: int,
    user_id: UUID,
    role: str,
    content: str,
    db: AsyncSession,
) -> int:
    """
    Save a message to a conversation.

    Args:
        conversation_id: ID of the conversation
        user_id: UUID of the user (for ownership validation)
        role: Message role - must be 'user' or 'assistant'
        content: Message content
        db: Database session

    Returns:
        int: ID of the saved message

    Raises:
        ValueError: If role is invalid or content is empty
        PermissionError: If conversation doesn't belong to user
    """
    # Validate role
    if role not in ["user", "assistant"]:
        raise ValueError("role must be 'user' or 'assistant'")

    # Validate content
    if not content or content.strip() == "":
        raise ValueError("content cannot be empty")

    # Verify conversation ownership
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")

    if conversation.user_id != user_id:
        raise PermissionError("Conversation does not belong to user")

    # Create message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
    )

    db.add(message)

    # Update conversation's updated_at timestamp
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)

    return message.id


async def load_history(
    conversation_id: int,
    user_id: UUID,
    db: AsyncSession,
    offset: int = 0,
    limit: int = None,
) -> List[Dict[str, Any]]:
    """
    Load conversation history with optional pagination.

    Args:
        conversation_id: ID of the conversation
        user_id: UUID of the user (for ownership validation)
        db: Database session
        offset: Number of messages to skip (default: 0)
        limit: Maximum number of messages to return (default: None - all messages)

    Returns:
        List of message dictionaries with keys:
            - id: Message ID
            - role: 'user' or 'assistant'
            - content: Message content
            - created_at: ISO format timestamp

    Raises:
        ValueError: If conversation doesn't exist
        PermissionError: If conversation doesn't belong to user
    """
    # Verify conversation exists and belongs to user
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise ValueError("Conversation not found")

    if conversation.user_id != user_id:
        raise PermissionError("Conversation does not belong to user")

    # Load messages ordered by creation time with pagination
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(offset)
    )

    # Only add limit if specified
    if limit is not None:
        statement = statement.limit(limit)

    result = await db.execute(statement)
    messages = result.scalars().all()

    # Format messages as dictionaries (eagerly convert to avoid lazy loading issues)
    formatted_messages = []
    for msg in messages:
        try:
            formatted_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            })
        except Exception as e:
            print(f"Error formatting message {msg.id if hasattr(msg, 'id') else 'unknown'}: {e}")
            raise

    return formatted_messages


async def validate_conversation_ownership(
    conversation_id: int,
    user_id: UUID,
    db: AsyncSession,
) -> bool:
    """
    Validate that a conversation belongs to a specific user.

    Args:
        conversation_id: ID of the conversation
        user_id: UUID of the user
        db: Database session

    Returns:
        bool: True if conversation belongs to user, False otherwise

    Raises:
        ValueError: If conversation doesn't exist
    """
    conversation = await db.get(Conversation, conversation_id)

    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")

    return conversation.user_id == user_id
