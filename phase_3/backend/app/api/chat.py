"""
Chat API endpoint for Phase 3 AI-powered task management.

Implements stateless conversation processing with:
- JWT authentication
- Conversation persistence
- Gemini AI Agent integration
- MCP tool execution
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.auth.jwt_handler import verify_jwt_token, get_current_user_id
from app.middleware.rate_limiter import check_rate_limit
from app.services.conversation_loader import (
    create_conversation,
    save_message,
    load_history,
)
from app.services.agent_runner import process_message
from app.services.mcp_service import get_mcp_service


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., description="User's message")
    conversation_id: Optional[int] = Field(None, description="Conversation ID (null for new conversation)")

    @validator("message")
    def validate_message(cls, v):
        """Validate message is not empty and within length limits."""
        if not v or v.strip() == "":
            raise ValueError("message cannot be empty")

        if len(v) > 5000:
            raise ValueError("message cannot exceed 5000 characters")

        return v.strip()

    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Validate conversation_id is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("conversation_id must be a positive integer")

        return v


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: int = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: List[Dict[str, Any]] = Field(default=[], description="MCP tool calls made")


# ============================================================================
# Chat Endpoint
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
    _rate_limit: None = Depends(check_rate_limit),
) -> ChatResponse:
    """
    Process a chat message with AI-powered task management.

    This endpoint implements a fully stateless request cycle:
    1. Verify JWT and extract user_id
    2. Check rate limits (T131: 10 requests per minute)
    3. Create new conversation or load existing one
    4. Load conversation history from database
    5. Persist user message
    6. Run AI agent with history + new message
    7. Execute MCP tool calls (e.g., add_task)
    8. Persist assistant response
    9. Return response + conversation_id

    Args:
        request: ChatRequest with message and optional conversation_id
        db: Database session (injected)
        user_id: User ID from JWT (injected)
        _rate_limit: Rate limit check (injected)

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException 400: Invalid request (empty message, etc.)
        HTTPException 401: Invalid/expired JWT token
        HTTPException 429: Rate limit exceeded (T131)
        HTTPException 500: Internal server error
    """
    try:
        # =====================================================================
        # Step 1: Conversation Management
        # =====================================================================

        conversation_id = request.conversation_id

        if conversation_id is None:
            # Create new conversation
            conversation_id = await create_conversation(user_id=user_id, db=db)
        else:
            # Validate conversation belongs to user
            try:
                # This will raise PermissionError if conversation doesn't belong to user
                await load_history(conversation_id, user_id, db)
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conversation does not belong to user"
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

        # =====================================================================
        # Step 2: Load Conversation History
        # =====================================================================

        conversation_history = await load_history(
            conversation_id=conversation_id,
            user_id=user_id,
            db=db,
        )

        # =====================================================================
        # Step 3: Persist User Message
        # =====================================================================

        await save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=request.message,
            db=db,
        )

        # =====================================================================
        # Step 4: Run AI Agent
        # =====================================================================

        try:
            # Get MCP service instance (integrated - direct tool calls, PDF compliant)
            mcp_client = get_mcp_service()

            agent_result = await process_message(
                user_id=user_id,
                message=request.message,
                conversation_history=conversation_history,
                mcp_client=mcp_client,
            )

            assistant_response = agent_result["response"]
            tool_calls = agent_result.get("tool_calls", [])

        except Exception as e:
            # Gemini API error handling
            print(f"Gemini API error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The AI service is temporarily unavailable. Please try again in a moment."
            )

        # =====================================================================
        # Step 5: Persist Assistant Response
        # =====================================================================

        await save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=assistant_response,
            db=db,
        )

        # =====================================================================
        # Step 6: Return Response
        # =====================================================================

        return ChatResponse(
            conversation_id=conversation_id,
            response=assistant_response,
            tool_calls=tool_calls,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


# ============================================================================
# Conversation History Endpoint
# ============================================================================

@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Get conversation history for a specific conversation.

    Args:
        conversation_id: ID of the conversation
        db: Database session (injected)
        user_id: User ID from JWT (injected)

    Returns:
        Dictionary with 'messages' list

    Raises:
        HTTPException 403: Conversation doesn't belong to user
        HTTPException 404: Conversation not found
    """
    try:
        history = await load_history(
            conversation_id=conversation_id,
            user_id=user_id,
            db=db,
        )

        return {"messages": history}

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to user"
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error loading conversation history: {e}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load conversation history: {str(e)}"
        )


# ============================================================================
# New Conversation Endpoint
# ============================================================================

@router.post("/conversations")
async def create_new_conversation(
    db: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Create a new conversation for the user.

    Args:
        db: Database session (injected)
        user_id: User ID from JWT (injected)

    Returns:
        Dictionary with 'conversation_id'
    """
    try:
        conversation_id = await create_conversation(user_id=user_id, db=db)

        return {"conversation_id": conversation_id}

    except Exception as e:
        print(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


# ============================================================================
# Get User's Active/Latest Conversation
# ============================================================================

@router.get("/conversations/active")
async def get_active_conversation(
    db: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Get the user's most recent active conversation.

    This is used to restore chat history when user logs back in.

    Args:
        db: Database session (injected)
        user_id: User ID from JWT (injected)

    Returns:
        Dictionary with 'conversation_id' and 'messages', or null if no conversation exists
    """
    from sqlalchemy import select, desc
    from app.models import Conversation

    try:
        # Find user's most recent conversation
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.is_active == True)
            .order_by(desc(Conversation.updated_at))
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if conversation is None:
            return {"conversation_id": None, "messages": []}

        # Load conversation history
        history = await load_history(
            conversation_id=conversation.id,
            user_id=user_id,
            db=db,
        )

        return {
            "conversation_id": conversation.id,
            "messages": history
        }

    except Exception as e:
        print(f"Error getting active conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active conversation"
        )
