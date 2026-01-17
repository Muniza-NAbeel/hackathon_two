"""
Authentication dependencies for FastAPI routes

Provides reusable authentication dependencies for route protection.
"""
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlmodel import Session
from app.db.database import get_session
from app.auth.jwt_handler import get_current_user_id


# Type aliases for dependency injection
AuthenticatedUserId = Annotated[UUID, Depends(get_current_user_id)]
DatabaseSession = Annotated[Session, Depends(get_session)]


def require_auth(user_id: AuthenticatedUserId) -> UUID:
    """
    Require authentication for a route.

    This is a simple pass-through dependency that requires authentication.
    Use this when you need to protect a route but don't need the user data.

    Args:
        user_id: Authenticated user ID from JWT token

    Returns:
        UUID: User ID

    Example:
        @app.get("/protected", dependencies=[Depends(require_auth)])
        def protected_route():
            return {"message": "You are authenticated"}
    """
    return user_id


# Example usage in routes:
#
# @app.get("/my-tasks")
# def get_my_tasks(
#     user_id: AuthenticatedUserId,
#     session: DatabaseSession
# ):
#     tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
#     return tasks
#
# @app.post("/tasks")
# def create_task(
#     task_data: TaskCreate,
#     user_id: AuthenticatedUserId,
#     session: DatabaseSession
# ):
#     task = Task(**task_data.dict(), user_id=user_id)
#     session.add(task)
#     session.commit()
#     return task
