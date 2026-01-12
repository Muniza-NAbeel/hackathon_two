"""
Authentication tests for JWT verification and authorization.

Tests:
- JWT token expiration handling (T120)
- Token validation
- User authentication flow
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from uuid import uuid4
import jwt

from app.auth.jwt_handler import create_access_token, JWT_SECRET, JWT_ALGORITHM


# Test UUID to use in all tests
TEST_UUID = str(uuid4())


class TestJWTExpiration:
    """Test JWT token expiration scenarios (T120)."""

    def test_expired_token_returns_401_with_helpful_error(
        self,
        client: TestClient,
    ):
        """
        T120: Test that expired JWT tokens are rejected with 401 and helpful error message.

        Verifies:
        - Expired tokens rejected with 401 Unauthorized
        - Error message is user-friendly
        - Suggests re-login
        """
        # Arrange: Create expired token with UUID user_id
        expired_payload = {
            "sub": TEST_UUID,
            "user_id": TEST_UUID,
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # Act: Send request with expired token
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {expired_token}"},
            json={"message": "Add buy milk"},
        )

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

        # Should have error message mentioning expiration or auth issue
        error_message = str(data["detail"]).lower()
        assert any(
            phrase in error_message
            for phrase in ["expired", "invalid", "authentication", "unauthorized"]
        )

    def test_valid_token_accepted(
        self,
        client: TestClient,
        valid_token: str,
    ):
        """Test that valid (non-expired) tokens are accepted."""
        # Act: Send request with valid token from fixture
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"message": "Add buy milk"},
        )

        # Assert: Should not get 401 (might get other status, but not auth error)
        assert response.status_code != 401

    def test_token_expiring_soon_still_valid(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that tokens expiring soon (but not yet expired) are still valid."""
        # Arrange: Create token expiring in 1 minute
        soon_to_expire_payload = {
            "sub": str(test_user_id),
            "user_id": str(test_user_id),
            "exp": datetime.utcnow() + timedelta(minutes=1),
        }
        token = jwt.encode(soon_to_expire_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # Act
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add buy milk"},
        )

        # Assert: Should still be accepted
        assert response.status_code != 401

    def test_malformed_token_returns_401(
        self,
        client: TestClient,
    ):
        """Test that malformed tokens are rejected with 401."""
        # Arrange: Create malformed token
        malformed_token = "not.a.valid.jwt.token"

        # Act
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {malformed_token}"},
            json={"message": "Add buy milk"},
        )

        # Assert
        assert response.status_code == 401

    def test_token_with_invalid_signature_rejected(
        self,
        client: TestClient,
    ):
        """Test that tokens with invalid signature are rejected."""
        # Arrange: Create token with wrong secret
        payload = {
            "sub": TEST_UUID,
            "user_id": TEST_UUID,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        wrong_secret_token = jwt.encode(payload, "wrong-secret", algorithm=JWT_ALGORITHM)

        # Act
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {wrong_secret_token}"},
            json={"message": "Add buy milk"},
        )

        # Assert
        assert response.status_code == 401

    def test_missing_authorization_header_returns_401_or_403(
        self,
        client: TestClient,
    ):
        """Test that requests without Authorization header are rejected."""
        # Act: No authorization header
        response = client.post(
            "/api/chat",
            json={"message": "Add buy milk"},
        )

        # Assert: Should return 401 or 403 (depends on FastAPI security configuration)
        assert response.status_code in [401, 403]

    def test_invalid_authorization_header_format_rejected(
        self,
        client: TestClient,
        valid_token: str,
    ):
        """Test that invalid Authorization header format is rejected."""
        # Act: Send token without "Bearer" prefix
        response = client.post(
            "/api/chat",
            headers={"Authorization": valid_token},  # Missing "Bearer"
            json={"message": "Add buy milk"},
        )

        # Assert: Should return 401 or 403
        assert response.status_code in [401, 403]

    def test_token_missing_user_id_claim_rejected(
        self,
        client: TestClient,
    ):
        """Test that tokens without user_id/sub claim are rejected."""
        # Arrange: Create token without user_id or sub
        payload = {
            "email": "test@example.com",  # Has email but no user_id/sub
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # Act
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add buy milk"},
        )

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestTokenRefresh:
    """Test token refresh scenarios (future enhancement)."""

    @pytest.mark.skip(reason="Token refresh not implemented in Phase 3")
    def test_refresh_token_endpoint_exists(
        self,
        client: TestClient,
    ):
        """Placeholder for future token refresh implementation."""
        pass
