"""
Notification Service - Phase 5 Event-Driven Architecture

Microservice that consumes reminder events from Kafka via Dapr Pub/Sub
and sends notifications to users.

Dapr Integration:
- Subscribes to 'reminders' topic via /dapr/subscribe
- Uses State Store for idempotency
- Receives events at /events/reminder endpoint
"""
import os
import structlog
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.health import router as health_router
from app.handlers.reminder import get_reminder_handler

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
    logger.info("notification_service_starting", version="1.0.0")

    # Startup
    pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
    logger.info("dapr_config", pubsub=pubsub_name)

    yield

    # Shutdown
    logger.info("notification_service_stopping")


# Create FastAPI application
app = FastAPI(
    title="Notification Service",
    description="Event-driven notification service for task reminders",
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

    Dapr calls this endpoint on startup to discover subscriptions.
    This service subscribes to the 'reminders' topic.
    """
    pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
    topic = os.getenv("REMINDERS_TOPIC", "reminders")

    subscriptions = [
        DaprSubscription(
            pubsubname=pubsub_name,
            topic=topic,
            route="/events/reminder",
            metadata={"rawPayload": "true"}
        )
    ]

    logger.info(
        "subscriptions_registered",
        pubsub=pubsub_name,
        topic=topic,
        count=len(subscriptions)
    )

    return subscriptions


# ============================================================================
# Event Endpoints
# ============================================================================

@app.post("/events/reminder")
async def handle_reminder_event(request: Request) -> Response:
    """
    Handle incoming reminder event from Dapr Pub/Sub.

    Dapr delivers CloudEvents to this endpoint.
    The handler processes with idempotency guarantee.
    """
    try:
        event_data = await request.json()

        logger.debug("reminder_event_received_raw", data=str(event_data)[:500])

        handler = get_reminder_handler()
        result = await handler.handle_reminder(event_data)

        if result.get("success"):
            # Return 200 to acknowledge the event
            return Response(status_code=200, content="OK")
        else:
            # Return 500 to trigger retry (if Dapr retry is configured)
            logger.error("reminder_processing_failed", result=result)
            return Response(status_code=500, content="Processing failed")

    except Exception as e:
        logger.error("reminder_endpoint_error", error=str(e))
        return Response(status_code=500, content=str(e))


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
