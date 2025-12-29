"""Authentication router with register, login, logout, and me endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import AuthResponse, ErrorCode, ErrorResponse, MessageResponse
from app.schemas.user import UserLogin, UserRead, UserRegister
from app.services.auth import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """
    Register a new user.

    Returns JWT token and user data on success.
    """
    try:
        user = await register_user(session, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorResponse(
                detail=str(e),
                code=ErrorCode.CONFLICT,
                field="email",
            ).model_dump(),
        )

    token, expires_at = create_access_token(user.id)

    return AuthResponse(
        user=UserRead.model_validate(user),
        token=token,
        expires_at=expires_at,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """
    Login with email and password.

    Returns JWT token and user data on success.
    """
    user = await authenticate_user(session, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                detail="Invalid email or password",
                code=ErrorCode.UNAUTHORIZED,
            ).model_dump(),
        )

    token, expires_at = create_access_token(user.id)

    return AuthResponse(
        user=UserRead.model_validate(user),
        token=token,
        expires_at=expires_at,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """
    Logout the current user.

    Note: JWT tokens are stateless, so we just return success.
    The client should discard the token.
    """
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserRead,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Get the current authenticated user."""
    return UserRead.model_validate(current_user)
