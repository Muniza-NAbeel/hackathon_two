"""
Idempotency Service using Dapr State Store

Prevents duplicate event processing by tracking processed event IDs.
Uses Dapr State Store with 24-hour TTL for automatic cleanup.
"""
import os
import httpx
import structlog
from datetime import datetime
from typing import Optional
from uuid import UUID

logger = structlog.get_logger(__name__)

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE", "statestore")
IDEMPOTENCY_TTL = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "86400"))  # 24 hours


class IdempotencyService:
    """
    Service for idempotent event processing.

    Uses Dapr State Store to track processed events:
    - Key pattern: {service}:processed:{event_id}
    - Value: ProcessedEvent record
    - TTL: 24 hours (configurable)

    Flow:
    1. Check if event was already processed
    2. If not, process the event
    3. Mark event as processed after successful processing
    """

    def __init__(
        self,
        service_name: str = "notification-service",
        state_store: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ):
        """
        Initialize idempotency service.

        Args:
            service_name: Name of this service (for key prefix)
            state_store: Dapr state store component name
            ttl_seconds: TTL for processed event records
        """
        self.service_name = service_name
        self.state_store = state_store or STATE_STORE_NAME
        self.ttl_seconds = ttl_seconds or IDEMPOTENCY_TTL
        self.dapr_url = f"http://localhost:{DAPR_HTTP_PORT}"

    def _make_key(self, event_id: str) -> str:
        """Generate state store key for event ID."""
        return f"{self.service_name}:processed:{event_id}"

    async def is_processed(self, event_id: str) -> bool:
        """
        Check if an event has already been processed.

        Args:
            event_id: Event ID to check

        Returns:
            True if event was already processed
        """
        key = self._make_key(event_id)
        url = f"{self.dapr_url}/v1.0/state/{self.state_store}/{key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)

                if response.status_code == 200 and response.text:
                    logger.debug(
                        "event_already_processed",
                        event_id=event_id,
                        service=self.service_name
                    )
                    return True
                elif response.status_code == 204:
                    return False
                else:
                    return False

        except httpx.RequestError as e:
            logger.warning(
                "idempotency_check_failed",
                event_id=event_id,
                error=str(e)
            )
            # On error, assume not processed to allow retry
            return False

    async def mark_processed(
        self,
        event_id: str,
        event_type: str,
        result: str = "success"
    ) -> bool:
        """
        Mark an event as processed.

        Args:
            event_id: Event ID to mark
            event_type: Type of event
            result: Processing result (success, skipped, error)

        Returns:
            True if marked successfully
        """
        key = self._make_key(event_id)
        url = f"{self.dapr_url}/v1.0/state/{self.state_store}"

        record = {
            "event_id": event_id,
            "event_type": event_type,
            "processed_at": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "result": result
        }

        state_item = [{
            "key": key,
            "value": record,
            "metadata": {
                "ttlInSeconds": str(self.ttl_seconds)
            }
        }]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=state_item,
                    timeout=5.0
                )

                if response.status_code in (200, 204):
                    logger.info(
                        "event_marked_processed",
                        event_id=event_id,
                        event_type=event_type,
                        result=result,
                        ttl=self.ttl_seconds
                    )
                    return True
                else:
                    logger.error(
                        "mark_processed_failed",
                        event_id=event_id,
                        status_code=response.status_code
                    )
                    return False

        except httpx.RequestError as e:
            logger.error(
                "mark_processed_error",
                event_id=event_id,
                error=str(e)
            )
            return False

    async def process_with_idempotency(
        self,
        event_id: str,
        event_type: str,
        processor_func
    ) -> tuple[bool, Optional[str]]:
        """
        Process event with idempotency guarantee.

        Args:
            event_id: Event ID
            event_type: Event type
            processor_func: Async function to process the event

        Returns:
            Tuple of (processed, result)
            - (True, "success") if processed successfully
            - (True, "skipped") if already processed
            - (False, "error") if processing failed
        """
        # Check if already processed
        if await self.is_processed(event_id):
            logger.info(
                "skipping_duplicate_event",
                event_id=event_id,
                event_type=event_type
            )
            return True, "skipped"

        # Process the event
        try:
            await processor_func()

            # Mark as processed
            await self.mark_processed(event_id, event_type, "success")
            return True, "success"

        except Exception as e:
            logger.error(
                "event_processing_failed",
                event_id=event_id,
                event_type=event_type,
                error=str(e)
            )
            # Don't mark as processed on error - allow retry
            return False, "error"


# Singleton instance
_idempotency_service: Optional[IdempotencyService] = None


def get_idempotency_service() -> IdempotencyService:
    """Get singleton IdempotencyService instance."""
    global _idempotency_service
    if _idempotency_service is None:
        _idempotency_service = IdempotencyService()
    return _idempotency_service
