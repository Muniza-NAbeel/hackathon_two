# Chat API Agent Specification (T145)

**Primary Responsibility:** Request orchestration, JWT verification, and conversation lifecycle management

## Overview

The Chat API Agent orchestrates the entire chat request lifecycle from HTTP request to response. It verifies authentication, loads conversation history, coordinates AI agent execution, persists messages, and returns formatted responses. This agent operates at the API boundary and ensures stateless request processing.

## Responsibilities

### 1. Request Orchestration
- Receive HTTP POST requests to `/api/chat`
- Parse and validate request payload
- Coordinate execution across multiple sub-agents:
  - JWT Verification (authentication)
  - Conversation History Loader (context)
  - AI Agent Runner (intelligence)
  - Message Persistence (storage)
- Return formatted HTTP responses

### 2. JWT Verification
- Extract JWT token from Authorization header
- Verify token signature and expiration
- Extract user_id from token payload
- Reject unauthorized requests with 401
- Use `get_current_user_id` dependency

### 3. Conversation Lifecycle Management
- Create new conversations on first message
- Load existing conversation history
- Append user message to conversation
- Append assistant response to conversation
- Update conversation metadata (last_message_at)

### 4. Stateless Request Cycle
- No server-side session management
- All context from database + JWT
- Each request is independent and self-contained
- Idempotent where applicable

## Inputs

### HTTP Request
```
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "message": "Add buy milk to my list",
    "conversation_id": 123  // Optional - creates new if omitted
}
```

### Request Schema (Pydantic)
```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int | None = None
```

### Authentication Context
```python
user_id: int  # Extracted from JWT via Depends(get_current_user_id)
```

## Outputs

### Success Response (200 OK)
```json
{
    "conversation_id": 123,
    "message_id": 456,
    "response": "I've added 'buy milk' to your task list.",
    "tool_calls": [
        {
            "tool_name": "add_task",
            "arguments": {"user_id": 789, "title": "buy milk"},
            "result": {"task_id": 101, "status": "created"}
        }
    ],
    "created_at": "2025-12-31T10:30:00Z"
}
```

### Error Responses

#### 401 Unauthorized
```json
{
    "detail": {
        "error": "token_expired",
        "message": "Your session has expired. Please log in again."
    }
}
```

#### 400 Bad Request
```json
{
    "detail": {
        "error": "validation_error",
        "message": "Invalid input: message is required",
        "field": "message"
    }
}
```

#### 429 Too Many Requests
```json
{
    "detail": {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please wait 42 seconds before trying again.",
        "retry_after": 42
    }
}
```

#### 503 Service Unavailable
```json
{
    "detail": {
        "error": "service_unavailable",
        "message": "The AI service is temporarily unavailable. Please try again in a moment."
    }
}
```

## Constraints

### Performance Constraints
- **Response Time:** < 2 seconds (p95 end-to-end)
  - JWT verification: < 1ms
  - History loading: < 50ms
  - AI agent execution: < 1.5s
  - Message persistence: < 100ms
  - Total: < 2 seconds
- **Concurrent Requests:** Support 100+ simultaneous chat requests
- **Rate Limiting:** 20 requests per user per minute

### Stateless Request Cycle
- **No Server-Side Sessions:** Each request is independent
- **Database as State Store:** All conversation state in PostgreSQL
- **JWT as Identity:** User identity from token (no session cookies)
- **Idempotent Operations:** Same message → different responses (AI non-determinism OK)

### Security Constraints
- **JWT Required:** All requests must include valid Authorization header
- **User Isolation:** Users can only access their own conversations
- **Input Sanitization:** Validate and sanitize all user inputs
- **Rate Limiting:** Enforce per-user rate limits
- **No PII Logging:** Don't log message content with user identifiers

## Architecture

### Request Flow

```
HTTP POST /api/chat
    ↓
[1] JWT Verification (get_current_user_id)
    ↓ (user_id extracted)
[2] Request Validation (ChatRequest schema)
    ↓
[3] Rate Limiting (check_rate_limit dependency)
    ↓
[4] Conversation Loading/Creation
    ├─→ conversation_id provided? Load existing
    └─→ No conversation_id? Create new
    ↓
[5] History Loading (load last 10 messages)
    ↓
[6] AI Agent Execution
    ├─→ OpenAI API call (intent detection)
    ├─→ MCP tool invocations (task operations)
    └─→ Response generation
    ↓
[7] Message Persistence
    ├─→ Save user message
    └─→ Save assistant response
    ↓
[8] Update Conversation Metadata
    ↓
[9] Format HTTP Response
    ↓
Return 200 OK with response data
```

### Endpoint Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt_handler import get_current_user_id
from app.middleware.rate_limiter import check_rate_limit
from app.services.conversation_service import ConversationService
from app.services.ai_agent_runner import AIAgentRunner
from app.skills.error_response_formatter import ErrorResponseFormatter
from app.db.database import get_session

router = APIRouter()

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),  # JWT verification
    _rate_limit: None = Depends(check_rate_limit),  # Rate limiting
    db: Session = Depends(get_session),
):
    """
    Chat endpoint with stateless request processing.

    Flow:
    1. JWT verification (automatic via dependency)
    2. Rate limiting (automatic via dependency)
    3. Load/create conversation
    4. Load conversation history
    5. Run AI agent
    6. Persist messages
    7. Return response
    """
    try:
        # Initialize services
        conversation_service = ConversationService(db)
        ai_agent = AIAgentRunner()

        # [4] Get or create conversation
        if request.conversation_id:
            # Load existing conversation
            conversation = conversation_service.get_conversation(
                conversation_id=request.conversation_id,
                user_id=user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponseFormatter.format_error(
                        error=ValueError("Conversation not found"),
                        error_type="not_found"
                    )
                )
        else:
            # Create new conversation
            conversation = conversation_service.create_conversation(
                user_id=user_id
            )

        # [5] Load conversation history (last 10 messages)
        history = conversation_service.load_history(
            conversation_id=conversation.id,
            user_id=user_id,
            limit=10
        )

        # [6] Run AI agent
        ai_response = await ai_agent.run(
            message=request.message,
            conversation_id=conversation.id,
            user_id=user_id,
            history=history,
            db=db
        )

        # [7] Persist messages
        user_message = conversation_service.add_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message
        )

        assistant_message = conversation_service.add_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=ai_response["response"]
        )

        # [8] Update conversation metadata
        conversation_service.update_last_message_time(
            conversation_id=conversation.id
        )

        # [9] Format response
        return {
            "conversation_id": conversation.id,
            "message_id": assistant_message.id,
            "response": ai_response["response"],
            "tool_calls": ai_response.get("tool_calls", []),
            "created_at": assistant_message.created_at.isoformat(),
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions (401, 404, etc.)

    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=400,
            detail=ErrorResponseFormatter.format_error(
                error=e,
                error_type="validation_error"
            )
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseFormatter.format_error(
                error=e,
                error_type="unknown_error"
            )
        )
```

## Error Handling

### Authentication Errors (401)
- **Token Missing:** Authorization header not provided
- **Token Expired:** JWT expiration time passed
- **Token Invalid:** Signature verification failed
- **User ID Missing:** Token payload doesn't contain user_id

### Validation Errors (400)
- **Message Empty:** message field is empty or missing
- **Message Too Long:** message exceeds 2000 characters
- **Invalid Conversation ID:** conversation_id is negative or invalid type

### Authorization Errors (403)
- **Conversation Access Denied:** User trying to access another user's conversation

### Not Found Errors (404)
- **Conversation Not Found:** conversation_id doesn't exist or was deleted

### Rate Limiting Errors (429)
- **Too Many Requests:** User exceeded rate limit (20 req/min)
- Include `retry_after` in response

### Service Errors (503)
- **AI Service Unavailable:** OpenAI API down or rate limited
- **MCP Server Unavailable:** Circuit breaker open
- **Database Unavailable:** PostgreSQL connection failure

## Testing Strategy

### Unit Tests
- Request validation (valid/invalid schemas)
- JWT verification (valid/expired/invalid tokens)
- Conversation creation and loading
- Message persistence
- Error handling for each error type

### Integration Tests
- End-to-end chat flow (new conversation)
- End-to-end chat flow (existing conversation)
- Rate limiting enforcement
- Concurrent requests (race conditions)
- Error propagation from sub-agents

### Acceptance Tests
- User sends message → conversation created → response returned
- User sends follow-up → history loaded → context-aware response
- Invalid token → 401 response
- Rate limit exceeded → 429 response
- AI service down → 503 response

### Performance Tests
- Response time < 2 seconds (p95)
- Handle 100 concurrent requests
- Rate limiter accuracy (20 req/min per user)

## Metrics and Monitoring

### Key Metrics
- **Request Rate:** Requests per second
- **Response Time:** p50, p95, p99 latency
- **Error Rate:** % of requests resulting in errors (by status code)
- **Authentication Failures:** 401 errors per minute
- **Rate Limit Hits:** 429 errors per minute
- **AI Agent Execution Time:** Time spent in AI agent

### Alerts
- Response time > 5 seconds (p95)
- Error rate > 5%
- 401 errors > 10/minute (possible attack)
- 503 errors > 5/minute (service degradation)

## Security Considerations

### Input Validation
```python
# Validate message length
if len(request.message) > 2000:
    raise ValueError("Message too long (max 2000 characters)")

# Sanitize input (remove dangerous characters if needed)
sanitized_message = sanitize_input(request.message)
```

### User Isolation
```python
# ✅ GOOD: Verify conversation ownership
conversation = db.exec(
    select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # Critical!
    )
).first()

# ❌ BAD: No ownership check (security vulnerability!)
conversation = db.exec(
    select(Conversation).where(Conversation.id == conversation_id)
).first()
```

### Rate Limiting
```python
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    _rate_limit: None = Depends(check_rate_limit),  # Enforces 20 req/min
    ...
):
    # Rate limiter runs BEFORE endpoint logic
    # 429 error raised if limit exceeded
    pass
```

### Error Message Security
```python
# ✅ GOOD: Generic user message, detailed logs
try:
    result = execute_query()
except DatabaseError as e:
    logger.error(f"Database query failed: {e}", exc_info=True)  # Detailed log
    raise HTTPException(
        500,
        detail="A database error occurred. Please try again."  # Generic message
    )

# ❌ BAD: Exposing internal details
except DatabaseError as e:
    raise HTTPException(500, detail=str(e))  # Exposes database structure!
```

## Related Documentation

- [AI Agent Spec](./ai_agent.md) - Agent execution
- [Conversation Agent Spec](./conversation_agent.md) - Message persistence
- [JWT Verification Skill](../skills/jwt_verification.md) - Authentication
- [Error Response Formatter](../skills/error_response_formatter.md) - Error handling
- [Rate Limiter](../docs/rate_limiter.md) - Rate limiting implementation
- [Architecture](../docs/architecture.md) - System design

---

**Agent Owner:** Backend Team
**Dependencies:** FastAPI, JWT Handler, AI Agent, Conversation Service, Rate Limiter
**Security Level:** Critical (API boundary, authentication, user data)
**Deployment:** Stateless, horizontally scalable
**Performance Target:** < 2s response time (p95), 100+ concurrent requests
**Statelessness:** Full statelessness - no server-side sessions
