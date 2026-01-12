# Error Response Formatter Skill (T142)

**Pattern for generating user-friendly error messages from system errors**

## Overview

Transforms technical error messages into user-friendly responses while preserving actionable information and maintaining security (no internal details exposed).

## Core Implementation

```python
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ErrorResponseFormatter:
    """Format error responses for user consumption."""

    # Error categories with user-friendly messages
    ERROR_MESSAGES = {
        # Authentication errors
        "token_expired": "Your session has expired. Please log in again.",
        "token_invalid": "Authentication failed. Please log in again.",
        "unauthorized": "You don't have permission to access this resource.",

        # Validation errors
        "validation_error": "Invalid input provided. Please check your request and try again.",
        "missing_field": "Required information is missing.",
        "invalid_format": "The provided data format is incorrect.",

        # Resource errors
        "not_found": "The requested resource was not found.",
        "already_exists": "This resource already exists.",

        # Rate limiting
        "rate_limit_exceeded": "Too many requests. Please wait {retry_after} seconds.",

        # Service errors
        "service_unavailable": "The service is temporarily unavailable. Please try again in a moment.",
        "mcp_server_down": "The task service is currently unavailable.",
        "openai_error": "The AI service is temporarily unavailable.",
        "database_error": "A database error occurred. Please try again.",

        # Generic
        "unknown_error": "An unexpected error occurred. Please try again.",
    }

    @staticmethod
    def format_error(
        error: Exception,
        error_type: str = "unknown_error",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format error into user-friendly response.

        Args:
            error: The exception that occurred
            error_type: Error category (from ERROR_MESSAGES keys)
            context: Additional context (e.g., retry_after, field_name)

        Returns:
            Formatted error response
        """
        # Log internal error details (for debugging)
        logger.error(f"Error occurred: {error_type} - {str(error)}", exc_info=True)

        # Get user-friendly message
        message = ErrorResponseFormatter.ERROR_MESSAGES.get(
            error_type,
            ErrorResponseFormatter.ERROR_MESSAGES["unknown_error"]
        )

        # Format message with context (e.g., retry_after)
        if context:
            try:
                message = message.format(**context)
            except KeyError:
                pass  # Use message as-is if formatting fails

        # Build response
        response = {
            "error": error_type,
            "message": message,
        }

        # Add actionable context (not internal details!)
        if context:
            # Only include safe context (no database errors, stack traces, etc.)
            safe_context = {
                k: v for k, v in context.items()
                if k in ["retry_after", "field_name", "max_length", "min_value"]
            }
            if safe_context:
                response["context"] = safe_context

        return response

    @staticmethod
    def format_validation_error(field: str, message: str) -> Dict[str, Any]:
        """Format field validation error."""
        return {
            "error": "validation_error",
            "message": f"Invalid {field}: {message}",
            "field": field,
        }

    @staticmethod
    def format_rate_limit_error(retry_after: int) -> Dict[str, Any]:
        """Format rate limit error with retry information."""
        return {
            "error": "rate_limit_exceeded",
            "message": f"Too many requests. Please wait {retry_after} seconds before trying again.",
            "retry_after": retry_after,
        }
```

## Usage Examples

### In API Endpoints

```python
from fastapi import HTTPException
from app.skills.error_response_formatter import ErrorResponseFormatter

formatter = ErrorResponseFormatter()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Process request
        result = await process_chat(request)
        return result

    except ValueError as e:
        # Validation error
        error_response = formatter.format_error(
            error=e,
            error_type="validation_error"
        )
        raise HTTPException(status_code=400, detail=error_response)

    except PermissionError as e:
        # Unauthorized
        error_response = formatter.format_error(
            error=e,
            error_type="unauthorized"
        )
        raise HTTPException(status_code=403, detail=error_response)

    except Exception as e:
        # Unknown error (logged with details, user sees generic message)
        error_response = formatter.format_error(
            error=e,
            error_type="unknown_error"
        )
        raise HTTPException(status_code=500, detail=error_response)
```

### With Context

```python
# Rate limit error with retry time
error_response = formatter.format_rate_limit_error(retry_after=45)
# Result:
# {
#   "error": "rate_limit_exceeded",
#   "message": "Too many requests. Please wait 45 seconds before trying again.",
#   "retry_after": 45
# }

# Validation error with field info
error_response = formatter.format_validation_error(
    field="title",
    message="must be between 1 and 200 characters"
)
# Result:
# {
#   "error": "validation_error",
#   "message": "Invalid title: must be between 1 and 200 characters",
#   "field": "title"
# }
```

### Frontend Error Display

```typescript
// React component error handling
function displayError(error: any) {
  if (error.detail) {
    const { error: errorType, message, retry_after } = error.detail;

    switch (errorType) {
      case 'rate_limit_exceeded':
        setError(`${message} Try again in ${retry_after}s.`);
        setRetryAfter(retry_after);
        break;

      case 'token_expired':
        setError(message);
        redirectToLogin();
        break;

      case 'validation_error':
        setError(message);
        if (error.detail.field) {
          highlightField(error.detail.field);
        }
        break;

      default:
        setError(message || 'An error occurred');
    }
  }
}
```

## Security Considerations

### ❌ Bad: Exposing Internal Details

```python
# DON'T DO THIS
@app.get("/api/tasks")
async def get_tasks():
    try:
        tasks = db.execute("SELECT * FROM tasks").all()
        return tasks
    except Exception as e:
        # SECURITY ISSUE: Exposes database structure and query
        raise HTTPException(500, detail=str(e))
        # User sees: "Table 'tasks' doesn't exist in database 'prod_db'"
```

### ✅ Good: Generic User Message, Detailed Logging

```python
# DO THIS
@app.get("/api/tasks")
async def get_tasks():
    try:
        tasks = db.execute("SELECT * FROM tasks").all()
        return tasks
    except Exception as e:
        # Log detailed error for debugging
        logger.error(f"Database query failed: {e}", exc_info=True)

        # Return generic message to user
        error_response = formatter.format_error(
            error=e,
            error_type="database_error"
        )
        raise HTTPException(500, detail=error_response)
        # User sees: "A database error occurred. Please try again."
```

## Error Response Examples

```python
# Success response (for comparison)
{
  "conversation_id": 123,
  "response": "I've added 'buy milk' to your task list.",
  "tool_calls": [...]
}

# Error responses
{
  "detail": {
    "error": "token_expired",
    "message": "Your session has expired. Please log in again."
  }
}

{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Please wait 42 seconds before trying again.",
    "retry_after": 42
  }
}

{
  "detail": {
    "error": "validation_error",
    "message": "Invalid title: must be between 1 and 200 characters",
    "field": "title"
  }
}

{
  "detail": {
    "error": "service_unavailable",
    "message": "The service is temporarily unavailable. Please try again in a moment."
  }
}
```

## Testing

```python
def test_format_error_basic():
    formatter = ErrorResponseFormatter()

    error = ValueError("Invalid input")
    response = formatter.format_error(error, "validation_error")

    assert response["error"] == "validation_error"
    assert "Invalid input provided" in response["message"]


def test_format_rate_limit_error():
    formatter = ErrorResponseFormatter()

    response = formatter.format_rate_limit_error(retry_after=30)

    assert response["error"] == "rate_limit_exceeded"
    assert "30 seconds" in response["message"]
    assert response["retry_after"] == 30


def test_format_validation_error():
    formatter = ErrorResponseFormatter()

    response = formatter.format_validation_error("email", "invalid format")

    assert response["error"] == "validation_error"
    assert response["field"] == "email"
    assert "Invalid email" in response["message"]


def test_no_internal_details_exposed():
    formatter = ErrorResponseFormatter()

    # Internal database error
    error = Exception("PostgreSQL: relation 'secret_table' does not exist")
    response = formatter.format_error(error, "database_error")

    # User should NOT see "secret_table" or PostgreSQL details
    assert "secret_table" not in response["message"]
    assert "PostgreSQL" not in response["message"]
    assert response["message"] == "A database error occurred. Please try again."
```

## Related Documentation

- [API Reference](../docs/api_reference.md) - Error response formats
- [Security](../docs/architecture.md#security) - Error handling security
- [Chat API Agent](../agents/chat_api_agent.md) - Error orchestration

---

**Skill Owner:** All Agents
**Security Level:** Critical (prevent information leakage)
**Logging:** All errors logged with full details server-side
**User Messages:** Generic, actionable, no internal details
