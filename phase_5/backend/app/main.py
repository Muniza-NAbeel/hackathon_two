"""
FastAPI Main Application for Phase 5 Event-Driven Architecture

This is the entry point for the Phase 5 backend.
Handles chat API endpoints and integrates with:
- OpenAI Agents SDK for natural language understanding
- MCP Server for task operations
- PostgreSQL for conversation persistence
- Dapr for event publishing (Kafka/Redpanda)
- CloudEvents for event schema
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.db import init_db
from app.db.database import warm_up_connection_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database, verify MCP tools
    - Shutdown: Close connections, cleanup resources
    """
    # Startup
    print("🚀 Starting Phase 3 AI Chatbot Backend...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print("🔧 MCP: Integrated mode (PDF compliant architecture)")

    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

    # Warm up connection pool (prevents first request timeout)
    try:
        await warm_up_connection_pool()
    except Exception as e:
        print(f"⚠️  Connection pool warm-up failed: {e}")

    # Verify MCP tools (integrated - no HTTP needed)
    try:
        from app.services.mcp_service import get_mcp_service
        mcp_service = get_mcp_service()
        status = mcp_service.get_status()
        print(f"✅ MCP Tools: {status['state']} ({status['type']})")
        print(f"   Available tools: {', '.join(status['tools'])}")
    except Exception as e:
        print(f"⚠️  MCP Tools verification failed: {e}")

    print("✅ Application startup complete")

    yield

    # Shutdown
    print("👋 Shutting down Phase 3 AI Chatbot Backend...")


# Create FastAPI application
app = FastAPI(
    title="Phase 3 AI Chatbot API",
    description="AI-powered task management chatbot using OpenAI Agents SDK and MCP",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phase 3 AI Chatbot API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status of backend, database, and MCP server

    Status Logic:
        - "healthy": All critical services (backend, database) operational
        - "degraded": Critical service failure
        - MCP is optional and does not affect overall status
    """
    from sqlalchemy import text

    health = {
        "status": "healthy",
        "backend": "ok",
        "database": "unknown",
        "mcp_server": "unknown",
    }

    # Check database (CRITICAL - affects overall status)
    try:
        from app.db.database import get_session
        async for session in get_session():
            # Use text() for async-compatible raw SQL
            await session.execute(text("SELECT 1"))
            health["database"] = "ok"
            break
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # Check MCP tools (integrated - no HTTP needed)
    try:
        from app.services.mcp_service import get_mcp_service
        mcp_service = get_mcp_service()
        status = mcp_service.get_status()
        if status["state"] == "integrated":
            health["mcp_server"] = "ok (integrated)"
        else:
            health["mcp_server"] = f"error: {status['state']}"
    except Exception as e:
        health["mcp_server"] = f"error: {str(e)}"

    return health


# ============================================================================
# API Routes
# ============================================================================

# Import routers
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.dapr import router as dapr_router
from app.api.internal import router as internal_router
from app.api.notifications import router as notifications_router
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router

# Register routers
app.include_router(health_router)  # Health checks
app.include_router(auth_router)  # Authentication (already has /api/auth prefix)
app.include_router(tasks_router)  # Task management (already has /api/{user_id}/tasks prefix)
app.include_router(chat_router)  # AI Chat
app.include_router(dapr_router)  # Dapr integration (Phase 5)
app.include_router(internal_router)  # Internal APIs (Phase 5)
app.include_router(notifications_router)  # Notifications (Phase 5)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} does not exist",
            "status_code": 404,
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500,
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
