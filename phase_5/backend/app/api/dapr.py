"""
Dapr Integration Endpoints

Provides Dapr-specific endpoints:
- /dapr/subscribe: Returns list of pubsub subscriptions (programmatic subscription)
- /dapr/config: Dapr configuration endpoints
"""
import os
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/dapr", tags=["dapr"])


class DaprSubscription(BaseModel):
    """Dapr pubsub subscription configuration"""
    pubsubname: str
    topic: str
    route: str
    metadata: dict = {}


@router.get("/subscribe", response_model=List[DaprSubscription])
async def get_subscriptions() -> List[DaprSubscription]:
    """
    Return Dapr Pub/Sub subscriptions for this service.

    Dapr calls this endpoint on startup to discover subscriptions.
    This enables programmatic subscription (vs declarative YAML).

    Note: Backend is an event PUBLISHER only.
    Primary consumers are notification-service and recurring-task-service.

    Returns:
        Empty list - backend does not subscribe to any topics
    """
    # Backend only publishes events, does not consume them
    # This prevents consumer group conflicts with other services
    return []


@router.get("/config")
async def get_dapr_config():
    """Return current Dapr configuration for debugging."""
    return {
        "pubsub_name": os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub"),
        "task_events_topic": os.getenv("TASK_EVENTS_TOPIC", "task-events"),
        "reminders_topic": os.getenv("REMINDERS_TOPIC", "reminders"),
        "dapr_http_port": os.getenv("DAPR_HTTP_PORT", "3500"),
        "events_enabled": os.getenv("EVENTS_ENABLED", "true"),
    }
