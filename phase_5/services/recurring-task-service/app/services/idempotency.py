"""
Idempotency Service for Recurring Task Service

Reuses the same pattern as notification-service.
Prevents duplicate task creation from the same event.
"""
import os
import httpx
import structlog
from datetime import datetime
from typing import Optional

logger = structlog.get_logger(__name__)

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE", "statestore")
IDEMPOTENCY_TTL = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "86400"))


class IdempotencyService:
    """Service for idempotent event processing."""

    def __init__(
        self,
        service_name: str = "recurring-task-service",
        state_store: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ):
        self.service_name = service_name
        self.state_store = state_store or STATE_STORE_NAME
        self.ttl_seconds = ttl_seconds or IDEMPOTENCY_TTL
        self.dapr_url = f"http://localhost:{DAPR_HTTP_PORT}"

    def _make_key(self, event_id: str) -> str:
        return f"{self.service_name}:processed:{event_id}"

    async def is_processed(self, event_id: str) -> bool:
        key = self._make_key(event_id)
        url = f"{self.dapr_url}/v1.0/state/{self.state_store}/{key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200 and response.text:
                    logger.debug("event_already_processed", event_id=event_id)
                    return True
                return False
        except httpx.RequestError as e:
            logger.warning("idempotency_check_failed", event_id=event_id, error=str(e))
            return False

    async def mark_processed(
        self,
        event_id: str,
        event_type: str,
        result: str = "success",
        new_task_id: Optional[int] = None
    ) -> bool:
        key = self._make_key(event_id)
        url = f"{self.dapr_url}/v1.0/state/{self.state_store}"

        record = {
            "event_id": event_id,
            "event_type": event_type,
            "processed_at": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "result": result,
            "new_task_id": new_task_id
        }

        state_item = [{
            "key": key,
            "value": record,
            "metadata": {"ttlInSeconds": str(self.ttl_seconds)}
        }]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=state_item, timeout=5.0)
                if response.status_code in (200, 204):
                    logger.info(
                        "event_marked_processed",
                        event_id=event_id,
                        new_task_id=new_task_id
                    )
                    return True
                return False
        except httpx.RequestError as e:
            logger.error("mark_processed_error", event_id=event_id, error=str(e))
            return False


_idempotency_service: Optional[IdempotencyService] = None


def get_idempotency_service() -> IdempotencyService:
    global _idempotency_service
    if _idempotency_service is None:
        _idempotency_service = IdempotencyService()
    return _idempotency_service
