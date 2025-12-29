"""Tests for task CRUD endpoints."""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User


@pytest_asyncio.fixture
async def test_task(session: AsyncSession, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        id=uuid4(),
        user_id=test_user.id,
        title="Test Task",
        description="Test description",
        completed=False,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@pytest.mark.asyncio
async def test_create_task_success(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test successful task creation."""
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "New Task",
            "description": "Task description",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "Task description"
    assert data["completed"] is False
    assert data["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_create_task_validation_error(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test task creation with empty title."""
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test listing tasks."""
    response = await client.get(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["id"] == str(test_task.id)
    assert data["total_count"] == 1


@pytest.mark.asyncio
async def test_list_tasks_with_filters(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test listing tasks with status filter."""
    # Test pending filter
    response = await client.get(
        f"/api/{test_user.id}/tasks?status=pending",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1  # test_task is not completed

    # Test completed filter
    response = await client.get(
        f"/api/{test_user.id}/tasks?status=completed",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 0


@pytest.mark.asyncio
async def test_get_task_success(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test getting a single task."""
    response = await client.get(
        f"/api/{test_user.id}/tasks/{test_task.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_task.id)
    assert data["title"] == test_task.title


@pytest.mark.asyncio
async def test_get_task_not_found(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test getting non-existent task."""
    response = await client.get(
        f"/api/{test_user.id}/tasks/{uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_forbidden(
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test getting another user's task returns 403."""
    # Create another user's task
    other_user_id = uuid4()
    other_task = Task(
        id=uuid4(),
        user_id=other_user_id,
        title="Other User's Task",
    )
    session.add(other_task)
    await session.commit()

    response = await client.get(
        f"/api/{test_user.id}/tasks/{other_task.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_task_success(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a task."""
    response = await client.put(
        f"/api/{test_user.id}/tasks/{test_task.id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_task_success(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a task."""
    response = await client.delete(
        f"/api/{test_user.id}/tasks/{test_task.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify task is deleted
    get_response = await client.get(
        f"/api/{test_user.id}/tasks/{test_task.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_complete(
    client: AsyncClient,
    test_user: User,
    test_task: Task,
    auth_headers: dict[str, str],
) -> None:
    """Test toggling task completion."""
    # Toggle to complete
    response = await client.patch(
        f"/api/{test_user.id}/tasks/{test_task.id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

    # Toggle back to incomplete
    response = await client.patch(
        f"/api/{test_user.id}/tasks/{test_task.id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_title_max_length(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test title maximum length validation (200 chars)."""
    # Valid 200 char title
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "A" * 200,
        },
    )
    assert response.status_code == 201

    # Invalid 201 char title
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "A" * 201,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_description_max_length(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test description maximum length validation (1000 chars)."""
    # Valid 1000 char description
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "Task",
            "description": "A" * 1000,
        },
    )
    assert response.status_code == 201

    # Invalid 1001 char description
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "Task",
            "description": "A" * 1001,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_title_rejected(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test that empty title is rejected."""
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "",
        },
    )
    assert response.status_code == 422

    # Whitespace-only title
    response = await client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={
            "title": "   ",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination(
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test task list pagination."""
    # Create 15 tasks
    for i in range(15):
        task = Task(
            user_id=test_user.id,
            title=f"Task {i + 1}",
        )
        session.add(task)
    await session.commit()

    # Get first page with 10 items
    response = await client.get(
        f"/api/{test_user.id}/tasks?page=1&per_page=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 10
    assert data["total_count"] == 15
    assert data["total_pages"] == 2
    assert data["page"] == 1

    # Get second page
    response = await client.get(
        f"/api/{test_user.id}/tasks?page=2&per_page=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 5
    assert data["page"] == 2
