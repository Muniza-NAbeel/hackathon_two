"""Authentication service with JWT and password hashing."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.user import UserRegister

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(user_id: UUID) -> tuple[str, datetime]:
    """
    Create a JWT access token with 7-day expiry.

    Returns:
        Tuple of (token, expires_at)
    """
    expires_at = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode = {
        "sub": str(user_id),
        "exp": expires_at,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(
        to_encode,
        settings.better_auth_secret,
        algorithm=settings.algorithm,
    )
    return token, expires_at


def decode_access_token(token: str) -> Optional[UUID]:
    """
    Decode and validate a JWT access token.

    Returns:
        User ID if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.algorithm],
        )
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            return None
        return UUID(user_id_str)
    except (JWTError, ValueError):
        return None


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email address."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(session: AsyncSession, user_data: UserRegister) -> User:
    """
    Register a new user.

    Raises:
        ValueError: If email is already registered
    """
    # Check if email already exists
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Returns:
        User if credentials are valid, None otherwise
    """
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
