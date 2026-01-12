"""FastAPI application entry point with CORS middleware."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting application startup sequence...")
    try:
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.error("Database connection details (without password):")
        db_url_safe = settings.database_url.split("@")[-1] if "@" in settings.database_url else "unknown"
        logger.error(f"  Host: {db_url_safe}")
        raise
    yield
    # Shutdown
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Todo Full-Stack Web Application API",
    description="RESTful API for multi-user task management with JWT authentication.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Register routers
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router

app.include_router(auth_router)
app.include_router(tasks_router)
