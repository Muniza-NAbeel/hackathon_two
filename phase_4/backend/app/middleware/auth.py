"""JWT authentication middleware."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.models.user import User
from app.services.auth import decode_access_token, get_user_by_id


class JWTBearer(HTTPBearer):
    """Custom JWT Bearer authentication scheme."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
                request
            )
        except HTTPException as e:
            # Convert 403 to 401 for missing credentials
            if e.status_code == status.HTTP_403_FORBIDDEN and self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise

        if credentials:
            if credentials.scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication scheme",
                    )
                return None
            return credentials.credentials
        return None


# Dependency for optional authentication
jwt_bearer_optional = JWTBearer(auto_error=False)

# Dependency for required authentication
jwt_bearer = JWTBearer(auto_error=True)


async def get_current_user(
    token: str = Depends(jwt_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Dependency to get the current authenticated user.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(jwt_bearer_optional),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Dependency to optionally get the current authenticated user.

    Returns None if not authenticated.
    """
    if token is None:
        return None

    user_id = decode_access_token(token)
    if user_id is None:
        return None

    return await get_user_by_id(session, user_id)


def verify_user_ownership(user_id: UUID, current_user: User) -> None:
    """
    Verify that the current user owns the resource.

    Raises:
        HTTPException: If user_id doesn't match current user
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
