"""
Rate Limiting Middleware (T131)

Implements rate limiting to prevent API abuse and ensure fair usage.

Features:
- In-memory rate limiting (per user)
- Configurable limits via environment variables
- Clean up of expired entries
- Informative error messages with retry-after headers
"""

import os
import time
from typing import Dict, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Rate limit: 10 requests per minute per user (default)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
RATE_LIMIT_WINDOW_SECONDS = 60


# ============================================================================
# Rate Limiter Implementation
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.

    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(self, max_requests: int = RATE_LIMIT_PER_MINUTE, window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # Store request timestamps per user: {user_id: [timestamp1, timestamp2, ...]}
        self.requests: Dict[int, list] = defaultdict(list)

        # Track when we last cleaned up expired entries
        self.last_cleanup = datetime.now()

    def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """
        Check if request is allowed for user.

        Args:
            user_id: ID of the user making the request

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Periodic cleanup of old entries (every 5 minutes)
        if datetime.now() - self.last_cleanup > timedelta(minutes=5):
            self._cleanup()

        # Get user's request history
        user_requests = self.requests[user_id]

        # Remove requests outside the current window
        user_requests[:] = [req_time for req_time in user_requests if req_time > window_start]

        # Check if limit exceeded
        if len(user_requests) >= self.max_requests:
            # Calculate retry-after (time until oldest request expires)
            oldest_request = min(user_requests)
            retry_after = int(oldest_request + self.window_seconds - now) + 1

            logger.warning(
                f"Rate limit exceeded for user {user_id}: "
                f"{len(user_requests)} requests in {self.window_seconds}s window"
            )

            return False, retry_after

        # Allow request and record timestamp
        user_requests.append(now)

        return True, 0

    def _cleanup(self):
        """Clean up expired request records to prevent memory bloat."""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove users with no recent requests
        users_to_remove = []

        for user_id, requests in self.requests.items():
            # Remove expired requests
            requests[:] = [req_time for req_time in requests if req_time > window_start]

            # If no requests in window, mark user for removal
            if not requests:
                users_to_remove.append(user_id)

        # Remove users with no recent activity
        for user_id in users_to_remove:
            del self.requests[user_id]

        self.last_cleanup = datetime.now()

        logger.info(f"Rate limiter cleanup: removed {len(users_to_remove)} inactive users")

    def get_status(self, user_id: int) -> Dict[str, any]:
        """
        Get rate limit status for user.

        Args:
            user_id: User ID to check

        Returns:
            Dictionary with rate limit status
        """
        now = time.time()
        window_start = now - self.window_seconds

        user_requests = self.requests[user_id]
        recent_requests = [req for req in user_requests if req > window_start]

        return {
            "user_id": user_id,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "requests_made": len(recent_requests),
            "requests_remaining": max(0, self.max_requests - len(recent_requests)),
        }


# ============================================================================
# Global Rate Limiter Instance
# ============================================================================

_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter


# ============================================================================
# FastAPI Dependency Factory
# ============================================================================

def create_rate_limit_dependency():
    """
    Create a rate limit dependency that can be used with FastAPI Depends.

    Returns:
        A dependency function that checks rate limits
    """
    from app.auth.jwt_handler import get_current_user_id

    async def rate_limit_check(user_id: int = Depends(get_current_user_id)) -> None:
        """
        Check rate limits for the current user.

        Args:
            user_id: User ID from JWT (injected)

        Raises:
            HTTPException 429: If rate limit exceeded
        """
        rate_limiter = get_rate_limiter()

        is_allowed, retry_after = rate_limiter.is_allowed(user_id)

        if not is_allowed:
            # Get current status
            status_info = rate_limiter.get_status(user_id)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. You can make {status_info['max_requests']} requests per {status_info['window_seconds']} seconds.",
                    "retry_after": retry_after,
                    "limit": status_info['max_requests'],
                    "window": status_info['window_seconds'],
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(status_info['max_requests']),
                    "X-RateLimit-Remaining": str(status_info['requests_remaining']),
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                }
            )

        # Log rate limit status
        status_info = rate_limiter.get_status(user_id)
        logger.debug(
            f"Rate limit status for user {user_id}: "
            f"{status_info['requests_made']}/{status_info['max_requests']} requests used"
        )

    return rate_limit_check


# Create the dependency instance
check_rate_limit = create_rate_limit_dependency()
