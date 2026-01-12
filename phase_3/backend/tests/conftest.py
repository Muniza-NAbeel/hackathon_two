"""
Pytest configuration and fixtures for Phase 3 AI Chatbot Backend

Provides reusable fixtures for:
- Test database setup/teardown
- FastAPI test client
- Authentication mocking
- Sample data generation
"""
import os
import pytest
from typing import Generator, AsyncGenerator
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Set test environment BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["MCP_SERVER_URL"] = "http://localhost:8001"
os.environ["DEBUG"] = "false"

from app.main import app
from app.db.database import get_session
from app.models import Task, Conversation, Message, User
from app.auth.jwt_handler import create_access_token, JWT_SECRET, JWT_ALGORITHM


# ============================================================================
# Test UUIDs (consistent across tests)
# ============================================================================

TEST_USER_UUID = uuid4()
TEST_USER_UUID_2 = uuid4()
TEST_USER_UUID_STR = str(TEST_USER_UUID)
TEST_USER_UUID_STR_2 = str(TEST_USER_UUID_2)


# ============================================================================
# Sync Database Fixtures (for TestClient)
# ============================================================================

@pytest.fixture(name="engine")
def engine_fixture():
    """
    Create in-memory SQLite engine for testing.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """
    Create test database session.
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="db_session")
def db_session_fixture(session: Session) -> Session:
    """Alias for session fixture (sync version)."""
    return session


# ============================================================================
# Async Database Fixtures (for async service tests)
# ============================================================================

@pytest.fixture(name="async_engine")
async def async_engine_fixture():
    """Create async in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(name="async_session")
async def async_session_fixture(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session_local = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_local() as session:
        yield session


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture(name="test_user_id")
def test_user_id_fixture(session: Session) -> UUID:
    """Create a test user and return their UUID"""
    user = User(
        id=TEST_USER_UUID,
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password_here",
        name="Test User",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.id


@pytest.fixture(name="test_user_id_str")
def test_user_id_str_fixture(session: Session) -> str:
    """Create a test user and return their UUID as string"""
    user = User(
        id=TEST_USER_UUID,
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password_here",
        name="Test User",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return str(user.id)


@pytest.fixture(name="async_test_user_id")
async def async_test_user_id_fixture(async_session: AsyncSession) -> UUID:
    """Create a test user in async session and return their UUID"""
    user = User(
        id=TEST_USER_UUID,
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password_here",
        name="Test User",
        created_at=datetime.utcnow()
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user.id


@pytest.fixture(name="test_user_id_2")
def test_user_id_2_fixture(session: Session) -> UUID:
    """Create a second test user for multi-user tests"""
    user = User(
        id=TEST_USER_UUID_2,
        email="test2@example.com",
        hashed_password="$2b$12$test_hashed_password_here",
        name="Test User 2",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.id


@pytest.fixture(name="valid_token")
def valid_token_fixture(test_user_id: UUID) -> str:
    """Create a valid JWT token for testing"""
    return create_access_token({"sub": str(test_user_id), "user_id": str(test_user_id)})


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(valid_token: str) -> dict:
    """Return authentication headers with valid token"""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture(name="expired_token")
def expired_token_fixture(test_user_id: UUID) -> str:
    """Create an expired JWT token for testing"""
    return create_access_token(
        {"sub": str(test_user_id), "user_id": str(test_user_id)},
        expires_delta=timedelta(hours=-1)  # Expired 1 hour ago
    )


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with test database.
    """
    # Create async generator wrapper for sync session
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture(name="sample_task")
def sample_task_fixture(session: Session, test_user_id: UUID) -> Task:
    """Create a sample task for testing."""
    task = Task(
        user_id=test_user_id,
        title="Test Task",
        description="This is a test task",
        status="pending",
        priority="medium",
        completed=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="sample_conversation")
def sample_conversation_fixture(session: Session, test_user_id: UUID) -> Conversation:
    """Create a sample conversation for testing."""
    conversation = Conversation(
        user_id=test_user_id,
        title="Test Conversation",
        is_active=True,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@pytest.fixture(name="test_conversation_id")
def test_conversation_id_fixture(session: Session, test_user_id: UUID) -> int:
    """Create a test conversation and return its ID (sync version)."""
    conversation = Conversation(
        user_id=test_user_id,
        title="Test Conversation",
        is_active=True,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation.id


@pytest.fixture(name="async_test_conversation_id")
async def async_test_conversation_id_fixture(async_session: AsyncSession, async_test_user_id: UUID) -> int:
    """Create a test conversation and return its ID (async version)."""
    conversation = Conversation(
        user_id=async_test_user_id,
        title="Test Conversation",
        is_active=True,
    )
    async_session.add(conversation)
    await async_session.commit()
    await async_session.refresh(conversation)
    return conversation.id


@pytest.fixture(name="sample_message")
def sample_message_fixture(session: Session, sample_conversation: Conversation, test_user_id: UUID) -> Message:
    """Create a sample message for testing."""
    message = Message(
        conversation_id=sample_conversation.id,
        user_id=test_user_id,
        role="user",
        content="Hello, AI!",
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# ============================================================================
# MCP Mock Fixtures
# ============================================================================

@pytest.fixture(name="mock_mcp_client")
def mock_mcp_client_fixture():
    """Mock MCP client for testing without actual MCP server."""
    mock_client = Mock()
    mock_client.call_tool = AsyncMock(return_value={
        "success": True,
        "message": "Task created successfully",
        "data": {
            "task_id": 1,
            "title": "Test Task",
            "status": "pending"
        }
    })
    return mock_client


@pytest.fixture(name="mock_gemini")
def mock_gemini_fixture():
    """Mock Gemini API for testing without actual API calls."""
    with patch('app.services.agent_runner.openai_client') as mock:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I've added that task for you!"
        mock.chat.completions.create = Mock(return_value=mock_response)
        yield mock


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_tables(session: Session):
    """Clean up tables after each test."""
    yield
    # Cleanup after test
    try:
        session.rollback()
    except:
        pass
