"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """Test successful user registration."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, test_user: User
) -> None:
    """Test registration with existing email fails."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "securepassword123",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    """Test registration with invalid email format."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    """Test registration with password less than 8 characters."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User) -> None:
    """Test successful login."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    client: AsyncClient, test_user: User
) -> None:
    """Test login with wrong password."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """Test login with non-existent email."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_success(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Test successful logout."""
    response = await client.post("/api/auth/logout", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_logout_unauthenticated(client: AsyncClient) -> None:
    """Test logout without auth token."""
    response = await client.post("/api/auth/logout")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test getting current user info."""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client: AsyncClient) -> None:
    """Test getting current user without auth token."""
    response = await client.get("/api/auth/me")

    assert response.status_code == 401
