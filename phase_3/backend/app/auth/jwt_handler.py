"""
JWT Token Handler for Phase 3 AI Chatbot

Provides JWT token verification and user ID extraction using Better Auth format from Phase 2.
"""

import os
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings


# ============================================================================
# Configuration
# ============================================================================

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

# HTTP Bearer security scheme
security = HTTPBearer()


# ============================================================================
# JWT Token Creation
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token (should include user_id or sub)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token({"sub": "user-uuid-here"})
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})

    # Ensure sub claim exists (standard JWT claim for subject/user_id)
    if "user_id" in to_encode and "sub" not in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])

    # Encode token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# ============================================================================
# JWT Verification
# ============================================================================

def verify_jwt_token(token: str) -> Dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string

    Returns:
        Dictionary with token payload (contains 'sub' with user_id)

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Debug logging
        print(f"[DEBUG] Verifying token with secret: {JWT_SECRET[:10]}...")
        print(f"[DEBUG] Algorithm: {JWT_ALGORITHM}")

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        print(f"[DEBUG] Token valid! Payload: {payload}")
        return payload

    except JWTError as e:
        print(f"[DEBUG] JWT Error: {e}")
        print(f"[DEBUG] Secret used: {JWT_SECRET[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract user ID from JWT token.

    This is a FastAPI dependency that:
    1. Extracts Bearer token from Authorization header
    2. Verifies the token
    3. Returns the user_id from the token payload

    Args:
        credentials: HTTP Authorization credentials (injected by FastAPI)

    Returns:
        UUID: User ID from token

    Raises:
        HTTPException 401: If token is missing, invalid, or expired

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: UUID = Depends(get_current_user_id)):
            return {"user_id": str(user_id)}
    """
    try:
        token = credentials.credentials
        payload = verify_jwt_token(token)

        # Extract user_id from 'sub' claim (standard JWT claim for subject)
        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert to UUID
        try:
            user_id = UUID(user_id_str) if isinstance(user_id_str, str) else user_id_str
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Catch any other exceptions
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
