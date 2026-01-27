"""
Recurring Task Service - Phase 5 Event-Driven Architecture

Microservice that consumes task.completed events from Kafka via Dapr
and creates next instances for recurring tasks.

Dapr Integration:
- Subscribes to 'task-events' topic via /dapr/subscribe
- Filters for task.completed events
- Uses Service Invocation to create tasks in backend
- Uses State Store for idempotency
"""
import os
import structlog
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.health import router as health_router
from app.handlers.task_completed import get_task_completed_handler

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("recurring_task_service_starting", version="1.0.0")

    pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
    backend_app_id = os.getenv("BACKEND_APP_ID", "chat-backend")
    logger.info("dapr_config", pubsub=pubsub_name, backend=backend_app_id)

    yield

    logger.info("recurring_task_service_stopping")


# Create FastAPI application
app = FastAPI(
    title="Recurring Task Service",
    description="Event-driven service for managing recurring tasks",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register health routes
app.include_router(health_router)


# ============================================================================
# Dapr Subscription Configuration
# ============================================================================

class DaprSubscription(BaseModel):
    """Dapr pubsub subscription"""
    pubsubname: str
    topic: str
    route: str
    metadata: dict = {}


@app.get("/dapr/subscribe", response_model=List[DaprSubscription])
async def get_subscriptions() -> List[DaprSubscription]:
    """
    Return Dapr Pub/Sub subscriptions.

    This service subscribes to 'task-events' topic to handle
    task.completed events for recurring tasks.
    """
    pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
    topic = os.getenv("TASK_EVENTS_TOPIC", "task-events")

    subscriptions = [
        DaprSubscription(
            pubsubname=pubsub_name,
            topic=topic,
            route="/events/task",
            metadata={"rawPayload": "true"}
        )
    ]

    logger.info(
        "subscriptions_registered",
        pubsub=pubsub_name,
        topic=topic
    )

    return subscriptions


# ============================================================================
# Event Endpoints
# ============================================================================

@app.post("/events/task")
async def handle_task_event(request: Request) -> Response:
    """
    Handle incoming task event from Dapr Pub/Sub.

    Filters for task.completed events and creates next recurring instance.
    """
    try:
        event_data = await request.json()

        logger.debug("task_event_received_raw", data=str(event_data)[:500])

        handler = get_task_completed_handler()
        result = await handler.handle_task_event(event_data)

        # Always return 200 to acknowledge the event
        # Even for ignored/skipped events, we don't want retries
        return Response(status_code=200, content="OK")

    except Exception as e:
        logger.error("task_event_endpoint_error", error=str(e))
        # Return 500 to trigger retry for unexpected errors
        return Response(status_code=500, content=str(e))


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "recurring-task-service",
        "version": "1.0.0",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
