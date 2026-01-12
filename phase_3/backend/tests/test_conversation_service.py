"""
Integration tests for conversation service.

These tests verify conversation creation, message persistence,
and conversation history loading functionality.
"""

import pytest
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.services.conversation_loader import (
    create_conversation,
    save_message,
    load_history,
)


class TestConversationCreation:
    """Test conversation creation functionality."""

    @pytest.mark.asyncio
    async def test_create_conversation_success(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test that a new conversation is created with correct user_id."""
        # Act
        conversation_id = await create_conversation(
            user_id=async_test_user_id, db=async_session
        )

        # Assert
        assert conversation_id is not None
        assert isinstance(conversation_id, int)

        # Verify in database
        conversation = await async_session.get(Conversation, conversation_id)
        assert conversation is not None
        assert conversation.user_id == async_test_user_id
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_conversation_multiple_for_same_user(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test that multiple conversations can be created for the same user."""
        # Act
        conv_id_1 = await create_conversation(user_id=async_test_user_id, db=async_session)
        conv_id_2 = await create_conversation(user_id=async_test_user_id, db=async_session)

        # Assert
        assert conv_id_1 != conv_id_2

        # Verify both exist in database
        conv_1 = await async_session.get(Conversation, conv_id_1)
        conv_2 = await async_session.get(Conversation, conv_id_2)
        assert conv_1.user_id == async_test_user_id
        assert conv_2.user_id == async_test_user_id

    @pytest.mark.asyncio
    async def test_create_conversation_invalid_user_id(self, async_session: AsyncSession):
        """Test that creating conversation with empty user_id raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            await create_conversation(user_id=None, db=async_session)


class TestMessagePersistence:
    """Test message persistence functionality."""

    @pytest.mark.asyncio
    async def test_save_message_success(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that messages are saved with correct conversation_id, role, and order."""
        # Arrange
        user_content = "Hello, I need help with my tasks"
        assistant_content = "I'd be happy to help! What would you like to do?"

        # Act - save user message
        user_msg_id = await save_message(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            role="user",
            content=user_content,
            db=async_session,
        )

        # Save assistant message
        assistant_msg_id = await save_message(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            role="assistant",
            content=assistant_content,
            db=async_session,
        )

        # Assert
        assert user_msg_id is not None
        assert assistant_msg_id is not None
        assert user_msg_id != assistant_msg_id

        # Verify in database
        user_msg = await async_session.get(Message, user_msg_id)
        assistant_msg = await async_session.get(Message, assistant_msg_id)

        assert user_msg.conversation_id == async_test_conversation_id
        assert user_msg.user_id == async_test_user_id
        assert user_msg.role == "user"
        assert user_msg.content == user_content
        assert user_msg.created_at is not None

        assert assistant_msg.conversation_id == async_test_conversation_id
        assert assistant_msg.user_id == async_test_user_id
        assert assistant_msg.role == "assistant"
        assert assistant_msg.content == assistant_content
        assert assistant_msg.created_at is not None

    @pytest.mark.asyncio
    async def test_save_message_chronological_order(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that messages are saved in chronological order."""
        # Arrange & Act - save multiple messages
        msg_ids = []
        for i in range(5):
            msg_id = await save_message(
                conversation_id=async_test_conversation_id,
                user_id=async_test_user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                db=async_session,
            )
            msg_ids.append(msg_id)

        # Assert - load history and verify order
        history = await load_history(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            db=async_session,
        )

        assert len(history) == 5
        for i, msg in enumerate(history):
            assert msg["content"] == f"Message {i}"

    @pytest.mark.asyncio
    async def test_save_message_invalid_role(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that invalid role raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="role must be 'user' or 'assistant'"):
            await save_message(
                conversation_id=async_test_conversation_id,
                user_id=async_test_user_id,
                role="invalid_role",
                content="Test message",
                db=async_session,
            )

    @pytest.mark.asyncio
    async def test_save_message_empty_content(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that empty content raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="content cannot be empty"):
            await save_message(
                conversation_id=async_test_conversation_id,
                user_id=async_test_user_id,
                role="user",
                content="",
                db=async_session,
            )


class TestConversationHistoryLoading:
    """Test conversation history loading functionality."""

    @pytest.mark.asyncio
    async def test_load_history_success(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that full conversation history is retrieved in order."""
        # Arrange - create conversation history
        messages_data = [
            ("user", "Hi, I need to manage my tasks"),
            ("assistant", "I can help you with that!"),
            ("user", "Add a task to buy groceries"),
            ("assistant", "I've added 'buy groceries' to your task list."),
            ("user", "Show me my tasks"),
            ("assistant", "Here are your tasks: 1. buy groceries"),
        ]

        for role, content in messages_data:
            await save_message(
                conversation_id=async_test_conversation_id,
                user_id=async_test_user_id,
                role=role,
                content=content,
                db=async_session,
            )

        # Act
        history = await load_history(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            db=async_session,
        )

        # Assert
        assert len(history) == 6
        for i, msg in enumerate(history):
            expected_role, expected_content = messages_data[i]
            assert msg["role"] == expected_role
            assert msg["content"] == expected_content
            assert "created_at" in msg
            assert "id" in msg

    @pytest.mark.asyncio
    async def test_load_history_empty_conversation(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test loading history from conversation with no messages."""
        # Act
        history = await load_history(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            db=async_session,
        )

        # Assert
        assert history == []

    @pytest.mark.asyncio
    async def test_load_history_wrong_user(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that loading history with wrong user_id raises PermissionError."""
        from uuid import uuid4

        # Arrange - create some messages
        await save_message(
            conversation_id=async_test_conversation_id,
            user_id=async_test_user_id,
            role="user",
            content="Test message",
            db=async_session,
        )

        # Act & Assert - use a different UUID
        with pytest.raises(PermissionError, match="Conversation does not belong to user"):
            await load_history(
                conversation_id=async_test_conversation_id,
                user_id=uuid4(),  # Different user
                db=async_session,
            )

    @pytest.mark.asyncio
    async def test_load_history_nonexistent_conversation(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test loading history from non-existent conversation raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Conversation not found"):
            await load_history(
                conversation_id=999999,
                user_id=async_test_user_id,
                db=async_session,
            )

    @pytest.mark.asyncio
    async def test_load_history_preserves_order_across_sessions(
        self, async_session: AsyncSession, async_test_user_id: UUID, async_test_conversation_id: int
    ):
        """Test that message order is preserved even when loaded multiple times."""
        # Arrange - create messages
        for i in range(10):
            await save_message(
                conversation_id=async_test_conversation_id,
                user_id=async_test_user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                db=async_session,
            )

        # Act - load history multiple times
        history_1 = await load_history(async_test_conversation_id, async_test_user_id, async_session)
        history_2 = await load_history(async_test_conversation_id, async_test_user_id, async_session)

        # Assert
        assert len(history_1) == 10
        assert len(history_2) == 10
        for i in range(10):
            assert history_1[i]["content"] == f"Message {i}"
            assert history_2[i]["content"] == f"Message {i}"
            assert history_1[i]["id"] == history_2[i]["id"]


class TestConversationPagination:
    """Test conversation history pagination (T124)."""

    @pytest.mark.asyncio
    async def test_large_conversation_pagination_efficient_loading(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """
        T124: Test conversation history pagination with 100+ messages.

        Verifies:
        - Efficient loading with offset/limit
        - Correct pagination results
        - Performance with large conversations
        - Chronological order maintained
        """
        # Arrange: Create conversation with 150 messages
        conversation_id = await create_conversation(user_id=async_test_user_id, db=async_session)

        # Create 150 messages (alternating user/assistant)
        for i in range(150):
            await save_message(
                conversation_id=conversation_id,
                user_id=async_test_user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message number {i}",
                db=async_session,
            )

        # Act: Load first page (50 messages, offset 0)
        page_1 = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=0,
            limit=50,
        )

        # Act: Load second page (50 messages, offset 50)
        page_2 = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=50,
            limit=50,
        )

        # Act: Load third page (50 messages, offset 100)
        page_3 = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=100,
            limit=50,
        )

        # Assert: Each page has correct number of messages
        assert len(page_1) == 50
        assert len(page_2) == 50
        assert len(page_3) == 50  # Remaining 50 messages

        # Assert: Pages are sequential and non-overlapping
        assert page_1[0]["content"] == "Message number 0"
        assert page_1[-1]["content"] == "Message number 49"
        assert page_2[0]["content"] == "Message number 50"
        assert page_2[-1]["content"] == "Message number 99"
        assert page_3[0]["content"] == "Message number 100"
        assert page_3[-1]["content"] == "Message number 149"

        # Assert: Chronological order maintained
        for i, message in enumerate(page_1):
            assert message["content"] == f"Message number {i}"
        for i, message in enumerate(page_2):
            assert message["content"] == f"Message number {i + 50}"
        for i, message in enumerate(page_3):
            assert message["content"] == f"Message number {i + 100}"

    @pytest.mark.asyncio
    async def test_pagination_with_custom_limit(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test pagination with different limit sizes."""
        # Arrange: Create conversation with 100 messages
        conversation_id = await create_conversation(user_id=async_test_user_id, db=async_session)

        for i in range(100):
            await save_message(
                conversation_id=conversation_id,
                user_id=async_test_user_id,
                role="user",
                content=f"Message {i}",
                db=async_session,
            )

        # Act: Load with limit=10
        page_small = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=0,
            limit=10,
        )

        # Act: Load with limit=100
        page_large = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=0,
            limit=100,
        )

        # Assert
        assert len(page_small) == 10
        assert len(page_large) == 100

    @pytest.mark.asyncio
    async def test_pagination_beyond_available_messages(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test pagination when offset is beyond available messages."""
        # Arrange: Create conversation with 50 messages
        conversation_id = await create_conversation(user_id=async_test_user_id, db=async_session)

        for i in range(50):
            await save_message(
                conversation_id=conversation_id,
                user_id=async_test_user_id,
                role="user",
                content=f"Message {i}",
                db=async_session,
            )

        # Act: Load with offset beyond available messages
        empty_page = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=100,  # Beyond 50 messages
            limit=50,
        )

        # Assert: Should return empty list
        assert len(empty_page) == 0

    @pytest.mark.asyncio
    async def test_pagination_performance_with_large_conversation(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test that pagination is efficient even with very large conversations."""
        import time

        # Arrange: Create conversation with 200 messages
        conversation_id = await create_conversation(user_id=async_test_user_id, db=async_session)

        for i in range(200):
            await save_message(
                conversation_id=conversation_id,
                user_id=async_test_user_id,
                role="user",
                content=f"Message {i}",
                db=async_session,
            )

        # Act: Load single page with timing
        start_time = time.time()
        page = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=50,
            limit=50,
        )
        end_time = time.time()

        # Assert: Loading should be fast (< 1000ms for test env)
        load_time_ms = (end_time - start_time) * 1000
        assert load_time_ms < 1000, f"Loading took {load_time_ms}ms, expected < 1000ms"

        # Assert: Correct page loaded
        assert len(page) == 50
        assert page[0]["content"] == "Message 50"

    @pytest.mark.asyncio
    async def test_pagination_with_mixed_message_roles(
        self, async_session: AsyncSession, async_test_user_id: UUID
    ):
        """Test pagination maintains correct role alternation."""
        # Arrange: Create conversation with alternating roles
        conversation_id = await create_conversation(user_id=async_test_user_id, db=async_session)

        for i in range(100):
            await save_message(
                conversation_id=conversation_id,
                user_id=async_test_user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                db=async_session,
            )

        # Act: Load second page
        page = await load_history(
            conversation_id=conversation_id,
            user_id=async_test_user_id,
            db=async_session,
            offset=40,
            limit=20,
        )

        # Assert: Roles alternate correctly
        assert len(page) == 20
        for i, message in enumerate(page):
            expected_role = "user" if (i + 40) % 2 == 0 else "assistant"
            assert message["role"] == expected_role
            assert message["content"] == f"Message {i + 40}"
