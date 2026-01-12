# Testing Agent Specification (T148)

**Primary Responsibility:** Test coverage, MCP tool validation, and statelessness verification

## Overview

The Testing Agent ensures comprehensive test coverage for Phase 3's chatbot implementation. It validates MCP tool functionality, verifies stateless operation, tests conversation persistence, and ensures all user stories meet acceptance criteria. This agent generates test skeletons, executes tests, and reports coverage metrics.

## Responsibilities

### 1. Test Coverage Generation
- Generate pytest skeletons for all Phase 3 components
- Create test cases for each user story (US6: Conversation persistence)
- Generate integration tests for API endpoints
- Create unit tests for skills and agents
- Ensure minimum 80% code coverage

### 2. MCP Tool Validation
- Test each MCP tool individually (add_task, list_tasks, etc.)
- Verify tool input validation
- Test tool error handling
- Validate user isolation (user A can't access user B's tasks)
- Test circuit breaker behavior

### 3. Statelessness Verification
- Verify no server-side state between requests
- Test conversation persistence across page reloads
- Validate that all state is in database or JWT
- Test concurrent requests (no race conditions)
- Verify idempotency where applicable

### 4. Conversation Persistence Testing
- Test conversation creation and loading
- Test message storage and retrieval
- Test conversation history pagination
- Verify chronological message ordering
- Test conversation ownership validation

### 5. AI Behavior Validation
- Test intent detection accuracy
- Test tool selection logic
- Validate parameter extraction
- Test response generation quality
- Verify error handling and fallbacks

## Inputs

### Test Configuration
```python
{
    "test_level": "unit" | "integration" | "e2e" | "all",
    "coverage_threshold": float = 0.80,  # 80% minimum
    "test_pattern": str = "test_*.py",
    "parallel": bool = True,
}
```

### Test Data
```python
{
    "test_users": List[Dict],  # Test user accounts
    "test_messages": List[str],  # Sample user messages
    "test_tasks": List[Dict],  # Sample tasks for validation
}
```

## Outputs

### Test Report
```python
{
    "total_tests": int,
    "passed": int,
    "failed": int,
    "skipped": int,
    "coverage": float,  # 0.0 - 1.0
    "duration": float,  # seconds
    "failures": List[Dict],  # Failed test details
}
```

### Coverage Report
```python
{
    "overall_coverage": float,
    "file_coverage": {
        "app/routes/chat.py": 0.95,
        "app/services/ai_agent.py": 0.88,
        # ... more files
    },
    "uncovered_lines": {
        "app/routes/chat.py": [42, 43, 55],
        # ... more files
    }
}
```

## Test Categories

### 1. Unit Tests

#### MCP Tools
```python
# test_mcp_tools.py

import pytest
from app.services.mcp_client import invoke_mcp_tool

@pytest.mark.asyncio
async def test_add_task_success(db_session, test_user):
    """Test successful task addition via MCP tool."""
    result = await invoke_mcp_tool(
        "add_task",
        {
            "user_id": test_user.id,
            "title": "Buy milk",
            "priority": "high",
        }
    )

    assert result["status"] == "success"
    assert result["data"]["title"] == "Buy milk"
    assert result["data"]["priority"] == "high"


@pytest.mark.asyncio
async def test_add_task_missing_title(test_user):
    """Test add_task with missing required field."""
    with pytest.raises(ValueError, match="title is required"):
        await invoke_mcp_tool(
            "add_task",
            {"user_id": test_user.id}  # Missing title
        )


@pytest.mark.asyncio
async def test_list_tasks_user_isolation(db_session, test_user, other_user):
    """Test that users only see their own tasks."""
    # User 1 creates task
    await invoke_mcp_tool(
        "add_task",
        {"user_id": test_user.id, "title": "User 1 task"}
    )

    # User 2 creates task
    await invoke_mcp_tool(
        "add_task",
        {"user_id": other_user.id, "title": "User 2 task"}
    )

    # User 1 lists tasks - should only see their own
    result = await invoke_mcp_tool(
        "list_tasks",
        {"user_id": test_user.id}
    )

    tasks = result["data"]["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["title"] == "User 1 task"
```

#### Conversation Service
```python
# test_conversation_service.py

import pytest
from app.services.conversation_service import ConversationService

def test_create_conversation(db_session, test_user):
    """Test conversation creation."""
    service = ConversationService(db_session)

    conv = service.create_conversation(user_id=test_user.id)

    assert conv.id is not None
    assert conv.user_id == test_user.id
    assert conv.title.startswith("Conversation on")


def test_add_message(db_session, test_user):
    """Test message addition to conversation."""
    service = ConversationService(db_session)

    # Create conversation
    conv = service.create_conversation(user_id=test_user.id)

    # Add message
    message = service.add_message(
        conversation_id=conv.id,
        user_id=test_user.id,
        role="user",
        content="Hello, assistant!"
    )

    assert message.id is not None
    assert message.role == "user"
    assert message.content == "Hello, assistant!"


def test_load_history_ownership(db_session, test_user, other_user):
    """Test that users can't access other users' conversations."""
    service = ConversationService(db_session)

    # User 1 creates conversation
    conv = service.create_conversation(user_id=test_user.id)

    # User 2 tries to access it
    with pytest.raises(PermissionError):
        service.load_history(
            conversation_id=conv.id,
            user_id=other_user.id
        )
```

#### AI Agent
```python
# test_ai_agent.py

import pytest
from app.services.ai_agent_runner import AIAgentRunner

@pytest.mark.asyncio
async def test_intent_detection_add_task(mock_openai_client):
    """Test intent detection for add_task."""
    agent = AIAgentRunner(mock_openai_client)

    result = await agent.run(
        message="Add buy milk to my list",
        conversation_id=123,
        user_id=456,
        db=None  # Mocked
    )

    assert result["intent"] == "add_task"
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["tool_name"] == "add_task"


@pytest.mark.asyncio
async def test_parameter_extraction(mock_openai_client):
    """Test parameter extraction from natural language."""
    agent = AIAgentRunner(mock_openai_client)

    result = await agent.run(
        message="Add high priority task: finish report by Friday",
        conversation_id=123,
        user_id=456,
        db=None
    )

    tool_call = result["tool_calls"][0]
    assert tool_call["arguments"]["title"] == "finish report"
    assert tool_call["arguments"]["priority"] == "high"
    assert "friday" in tool_call["arguments"]["due_date"].lower()
```

### 2. Integration Tests

#### Chat API Endpoint
```python
# test_chat_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint_success(test_user, jwt_token):
    """Test successful chat request."""
    response = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add buy milk"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "tool_calls" in data


def test_chat_endpoint_unauthorized():
    """Test chat endpoint without authentication."""
    response = client.post(
        "/api/chat",
        json={"message": "Add buy milk"}
    )

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "unauthorized"


def test_chat_endpoint_rate_limiting(test_user, jwt_token):
    """Test rate limiting enforcement."""
    # Send 21 requests (limit is 20/min)
    for i in range(21):
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {jwt_token}"},
            json={"message": f"Message {i}"}
        )

        if i < 20:
            assert response.status_code == 200
        else:
            # 21st request should be rate limited
            assert response.status_code == 429
            assert "retry_after" in response.json()["detail"]
```

#### Conversation Persistence
```python
# test_conversation_persistence.py

def test_conversation_persistence_across_requests(test_user, jwt_token):
    """Test that conversation persists across multiple requests."""
    # First message - creates new conversation
    response1 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add buy milk"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Second message - same conversation
    response2 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "message": "What's on my list?",
            "conversation_id": conversation_id
        }
    )
    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id

    # Verify history includes both messages
    history_response = client.get(
        f"/api/conversations/{conversation_id}/history",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert history_response.status_code == 200
    messages = history_response.json()["messages"]
    assert len(messages) >= 2  # At least user + assistant messages
```

### 3. Statelessness Tests

```python
# test_statelessness.py

def test_no_server_side_state(test_user, jwt_token):
    """Verify no server-side state between requests."""
    # Request 1
    response1 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add task 1"}
    )
    conv_id_1 = response1.json()["conversation_id"]

    # Request 2 (different conversation)
    response2 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add task 2"}  # No conversation_id - new conv
    )
    conv_id_2 = response2.json()["conversation_id"]

    # Conversations should be independent
    assert conv_id_1 != conv_id_2


@pytest.mark.asyncio
async def test_concurrent_requests_no_race_conditions(test_user, jwt_token):
    """Test concurrent requests don't interfere with each other."""
    import asyncio
    import httpx

    async def send_message(message: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/chat",
                headers={"Authorization": f"Bearer {jwt_token}"},
                json={"message": message}
            )
            return response.json()

    # Send 10 concurrent requests
    tasks = [send_message(f"Add task {i}") for i in range(10)]
    results = await asyncio.gather(*tasks)

    # All should succeed
    assert len(results) == 10
    for result in results:
        assert "conversation_id" in result
        assert "response" in result


def test_idempotent_conversation_loading(test_user, jwt_token):
    """Verify conversation loading is idempotent."""
    # Create conversation
    response1 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add task"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Load history multiple times
    history1 = client.get(
        f"/api/conversations/{conversation_id}/history",
        headers={"Authorization": f"Bearer {jwt_token}"}
    ).json()

    history2 = client.get(
        f"/api/conversations/{conversation_id}/history",
        headers={"Authorization": f"Bearer {jwt_token}"}
    ).json()

    # Results should be identical
    assert history1 == history2
```

### 4. User Story Acceptance Tests

```python
# test_user_stories.py

def test_us6_conversation_persistence(test_user, jwt_token):
    """
    US6: As a user, I want my conversation to persist across page reloads,
    so I don't lose context.

    Acceptance Criteria:
    - User sends message → conversation created
    - Page reload (simulated by new request with conversation_id) → history loads
    - Previous messages are displayed
    """
    # Step 1: User sends first message
    response1 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Add buy milk"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Step 2: User sends second message
    response2 = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "message": "Add finish report",
            "conversation_id": conversation_id
        }
    )
    assert response2.status_code == 200

    # Step 3: Simulate page reload - load conversation history
    history_response = client.get(
        f"/api/conversations/{conversation_id}/history",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert history_response.status_code == 200

    # Step 4: Verify previous messages are present
    messages = history_response.json()["messages"]
    assert len(messages) >= 4  # 2 user messages + 2 assistant responses

    # Verify chronological order
    user_messages = [msg for msg in messages if msg["role"] == "user"]
    assert "buy milk" in user_messages[0]["content"].lower()
    assert "finish report" in user_messages[1]["content"].lower()
```

## Test Fixtures

```python
# conftest.py

import pytest
from sqlmodel import Session, create_engine
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.auth.jwt_handler import create_jwt_token

@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    """Create another test user for isolation testing."""
    user = User(
        email="other@example.com",
        name="Other User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def jwt_token(test_user):
    """Create JWT token for test user."""
    return create_jwt_token(user_id=test_user.id)


@pytest.fixture
def mock_openai_client(mocker):
    """Mock OpenAI client for testing."""
    mock = mocker.Mock()
    # Configure mock responses
    mock.chat.completions.create.return_value = mocker.Mock(
        choices=[
            mocker.Mock(
                message=mocker.Mock(
                    content="I've added 'buy milk' to your task list.",
                    tool_calls=[
                        mocker.Mock(
                            function=mocker.Mock(
                                name="add_task",
                                arguments='{"title": "buy milk"}'
                            )
                        )
                    ]
                )
            )
        ]
    )
    return mock
```

## Coverage Requirements

### Minimum Coverage Targets
- **Overall:** 80%
- **Critical Paths:** 95% (authentication, MCP tools, conversation persistence)
- **API Endpoints:** 90%
- **Services/Agents:** 85%
- **Skills:** 90%
- **UI Components:** 70%

### Coverage Exclusions
- Third-party library code
- Configuration files
- Database migrations
- Development utilities

## Test Execution

### Run All Tests
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# User story acceptance tests
pytest tests/acceptance/
```

### Parallel Execution
```bash
pytest tests/ -n auto  # Auto-detect CPU cores
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ --cov=app --cov-fail-under=80
```

## Metrics and Monitoring

### Key Metrics
- **Test Count:** Total tests, per category
- **Pass Rate:** % of tests passing
- **Coverage:** Overall and per-file coverage
- **Test Duration:** Time to run full suite
- **Flaky Tests:** Tests with intermittent failures

### Alerts
- Test pass rate < 95%
- Coverage drops below 80%
- Test suite duration > 5 minutes
- Flaky test detected (3+ failures in 10 runs)

## Related Documentation

- [AI Agent Spec](./ai_agent.md) - Agent testing
- [MCP Agent Spec](./mcp_agent.md) - MCP tool testing
- [Chat API Agent](./chat_api_agent.md) - API endpoint testing
- [Conversation Agent](./conversation_agent.md) - Persistence testing
- [Architecture](../docs/architecture.md) - System design

---

**Agent Owner:** QA/DevOps Team
**Dependencies:** pytest, pytest-cov, pytest-asyncio, pytest-mock
**Coverage Target:** 80% overall, 95% critical paths
**CI/CD:** GitHub Actions (automated on every push)
**Performance Target:** < 5 minutes for full test suite
**Statelessness Validation:** All statelessness tests must pass
