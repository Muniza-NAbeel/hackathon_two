# JWT Verification Skill (T140)

**Pattern for extracting user_id from JWT with error handling**

## Overview

The JWT verification skill provides secure extraction of user identity from JWT tokens, with comprehensive error handling for expired, invalid, or malformed tokens.

## Responsibilities

- Verify JWT signature using shared secret
- Extract user_id from token payload
- Handle token expiration gracefully
- Validate token structure and claims
- Provide clear error messages for debugging

## Implementation Pattern

### Basic JWT Verification

```python
import jwt
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status

# Configuration (from environment)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        Decoded token payload (dict)

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_user_id_from_token(token: str) -> int:
    """
    Extract user_id from JWT token.

    Args:
        token: JWT token string

    Returns:
        user_id as integer

    Raises:
        HTTPException: If token invalid or user_id missing
    """
    payload = verify_jwt_token(token)

    # Extract user_id
    user_id = payload.get("user_id") or payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user_id claim"
        )

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id format in token"
        )
```

### FastAPI Dependency

```python
from fastapi import Depends, Header, HTTPException

async def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    FastAPI dependency to extract user_id from Authorization header.

    Usage:
        @app.get("/api/endpoint")
        async def endpoint(user_id: int = Depends(get_current_user_id)):
            # user_id is available here
            pass

    Args:
        authorization: Authorization header (format: "Bearer <token>")

    Returns:
        user_id as integer

    Raises:
        HTTPException 401: If authorization header missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    # Verify token and extract user_id
    return get_user_id_from_token(token)
```

## Usage Examples

### In API Endpoints

```python
from fastapi import APIRouter, Depends
from app.auth.jwt_handler import get_current_user_id

router = APIRouter()

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)  # Auto-extracted!
):
    """
    Chat endpoint with automatic JWT verification.

    The user_id parameter is automatically extracted from the
    Authorization header by the get_current_user_id dependency.
    """
    # user_id is validated and ready to use
    conversation = create_conversation(user_id=user_id)
    return {"conversation_id": conversation.id}


@router.get("/api/tasks")
async def get_tasks(user_id: int = Depends(get_current_user_id)):
    """List tasks for authenticated user."""
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return {"tasks": tasks}
```

### Manual Verification

```python
from app.auth.jwt_handler import verify_jwt_token, get_user_id_from_token

def process_authenticated_request(request):
    # Extract token from request
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return {"error": "Missing authorization"}

    token = auth_header.replace("Bearer ", "")

    # Verify and extract user_id
    try:
        user_id = get_user_id_from_token(token)
        return process_for_user(user_id)

    except HTTPException as e:
        return {"error": e.detail}
```

## Error Handling Patterns

### Comprehensive Error Handling

```python
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
    DecodeError,
    InvalidSignatureError
)

def verify_jwt_with_detailed_errors(token: str) -> dict:
    """Verify JWT with detailed error categorization."""

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"success": True, "payload": payload}

    except ExpiredSignatureError:
        return {
            "success": False,
            "error": "token_expired",
            "message": "Your session has expired. Please log in again.",
            "action": "redirect_to_login"
        }

    except InvalidSignatureError:
        return {
            "success": False,
            "error": "invalid_signature",
            "message": "Token signature is invalid",
            "action": "reject"
        }

    except DecodeError:
        return {
            "success": False,
            "error": "malformed_token",
            "message": "Token is malformed",
            "action": "reject"
        }

    except InvalidTokenError as e:
        return {
            "success": False,
            "error": "invalid_token",
            "message": str(e),
            "action": "reject"
        }
```

### Client-Side Error Handling

```typescript
// Frontend error handling
async function makeAuthenticatedRequest(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('jwt_token');

  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    const error = await response.json();

    if (error.detail.includes('expired')) {
      // Token expired - redirect to login
      localStorage.removeItem('jwt_token');
      window.location.href = '/login';
      throw new Error('Session expired. Please log in again.');
    }

    throw new Error(error.detail || 'Authentication failed');
  }

  return response.json();
}
```

## Security Best Practices

### Token Validation Checklist

```python
def validate_jwt_comprehensive(token: str, user_id: Optional[int] = None) -> bool:
    """
    Comprehensive JWT validation with security checks.

    Checks:
    - Signature validity
    - Expiration time
    - Not-before time (nbf)
    - Issuer (iss) if configured
    - Audience (aud) if configured
    - User ID match (if provided)
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": False,  # Enable if using audience claims
                "require_exp": True,
                "require_iat": True,
            }
        )

        # Verify user_id match if provided
        if user_id is not None:
            token_user_id = payload.get("user_id") or payload.get("sub")
            if int(token_user_id) != user_id:
                logger.warning(f"User ID mismatch: token={token_user_id}, expected={user_id}")
                return False

        # Additional custom validations
        # ...

        return True

    except Exception as e:
        logger.error(f"JWT validation failed: {e}")
        return False
```

### Secure Token Storage (Frontend)

```typescript
// Store token securely
function storeToken(token: string) {
  // Use httpOnly cookie in production (server-side)
  // For Phase 3, localStorage is acceptable (client-side SPA)

  localStorage.setItem('jwt_token', token);

  // Optional: Store expiration for client-side checks
  const payload = parseJwt(token);
  if (payload.exp) {
    localStorage.setItem('jwt_expires', payload.exp.toString());
  }
}

// Parse JWT without verification (client-side preview only)
function parseJwt(token: string) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );
  return JSON.parse(jsonPayload);
}

// Check if token is expired (client-side preview)
function isTokenExpired(): boolean {
  const exp = localStorage.getItem('jwt_expires');
  if (!exp) return true;

  const expirationTime = parseInt(exp) * 1000; // Convert to milliseconds
  return Date.now() >= expirationTime;
}
```

## Testing

```python
import pytest
import jwt
from datetime import datetime, timedelta

def test_verify_valid_token():
    # Create valid token
    payload = {
        "user_id": 123,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Verify
    result = verify_jwt_token(token)
    assert result["user_id"] == 123


def test_verify_expired_token():
    # Create expired token
    payload = {
        "user_id": 123,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Already expired
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_verify_invalid_signature():
    # Create token with different secret
    payload = {"user_id": 123}
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401


def test_get_user_id_from_token():
    payload = {
        "user_id": 456,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    user_id = get_user_id_from_token(token)
    assert user_id == 456


def test_get_user_id_missing_claim():
    # Token without user_id
    payload = {
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        get_user_id_from_token(token)

    assert "user_id claim" in exc_info.value.detail
```

## Performance Considerations

### Token Verification Overhead

- **CPU cost:** ~0.5-1ms per verification (signature check)
- **No database hit:** Stateless verification
- **Cache consideration:** Not needed for JWT (self-contained)

### Optimization Tips

```python
# Don't verify token multiple times in same request
# Use FastAPI dependency injection (verified once, cached)

# BAD: Multiple verifications
@app.get("/endpoint")
async def endpoint(authorization: str = Header(None)):
    user_id = get_user_id_from_token(authorization.replace("Bearer ", ""))  # 1st verification
    # ...
    user_id2 = get_user_id_from_token(authorization.replace("Bearer ", ""))  # 2nd verification (wasteful!)

# GOOD: Single verification via dependency
@app.get("/endpoint")
async def endpoint(user_id: int = Depends(get_current_user_id)):
    # Token verified once by FastAPI dependency system
    # user_id available throughout request
    pass
```

## Integration with Rate Limiter

```python
from app.middleware.rate_limiter import check_rate_limit

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),  # JWT verification
    _rate_limit: None = Depends(check_rate_limit)  # Rate limit (uses user_id)
):
    """
    Endpoint with both JWT verification and rate limiting.

    Order of execution:
    1. get_current_user_id extracts user_id from JWT
    2. check_rate_limit uses that user_id for rate limiting
    3. Endpoint logic executes if both pass
    """
    pass
```

## Related Documentation

- [Architecture](../docs/architecture.md) - Security design
- [API Reference](../docs/api_reference.md) - Authentication flows
- [Chat API Agent Spec](../agents/chat_api_agent.md) - Request orchestration

---

**Skill Owner:** Chat API Agent
**Dependencies:** PyJWT, FastAPI
**Security Level:** Critical (authentication boundary)
**Performance Target:** < 1ms verification time
