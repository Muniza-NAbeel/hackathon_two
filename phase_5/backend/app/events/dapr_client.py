"""
Dapr HTTP Client Wrapper

Provides async HTTP client for Dapr sidecar communication.
Dapr sidecar runs on localhost:3500 by default.
"""
import os
import httpx
import structlog
from typing import Any, Optional

logger = structlog.get_logger(__name__)


class DaprClient:
    """
    Async HTTP client for Dapr sidecar communication.

    Dapr Building Blocks used:
    - Pub/Sub: Publish events to message broker (Kafka/Redpanda)
    - State: Store/retrieve state for idempotency
    - Service Invocation: Call other services

    Environment Variables:
    - DAPR_HTTP_PORT: Dapr sidecar HTTP port (default: 3500)
    - DAPR_GRPC_PORT: Dapr sidecar gRPC port (default: 50001)
    """

    def __init__(
        self,
        dapr_port: Optional[int] = None,
        timeout: float = 30.0
    ):
        """
        Initialize Dapr client.

        Args:
            dapr_port: Dapr sidecar HTTP port (default from env or 3500)
            timeout: Request timeout in seconds
        """
        self.dapr_port = dapr_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.base_url = f"http://localhost:{self.dapr_port}"
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: dict,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Publish event to Dapr Pub/Sub.

        Args:
            pubsub_name: Name of the pub/sub component (e.g., "kafka-pubsub")
            topic: Topic name (e.g., "task-events")
            data: Event data (CloudEvents format)
            metadata: Optional metadata headers

        Returns:
            True if published successfully, False otherwise
        """
        client = await self._get_client()
        url = f"/v1.0/publish/{pubsub_name}/{topic}"

        try:
            headers = {}
            if metadata:
                for key, value in metadata.items():
                    headers[f"metadata.{key}"] = str(value)

            response = await client.post(url, json=data, headers=headers)

            if response.status_code in (200, 204):
                logger.info(
                    "event_published",
                    pubsub=pubsub_name,
                    topic=topic,
                    event_id=data.get("id"),
                    event_type=data.get("type")
                )
                return True
            else:
                logger.error(
                    "event_publish_failed",
                    pubsub=pubsub_name,
                    topic=topic,
                    status_code=response.status_code,
                    response=response.text
                )
                return False

        except httpx.RequestError as e:
            logger.error(
                "dapr_request_error",
                pubsub=pubsub_name,
                topic=topic,
                error=str(e)
            )
            return False

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """
        Get state from Dapr State Store.

        Args:
            store_name: Name of state store component
            key: State key

        Returns:
            State value or None if not found
        """
        client = await self._get_client()
        url = f"/v1.0/state/{store_name}/{key}"

        try:
            response = await client.get(url)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                return None
            else:
                logger.warning(
                    "state_get_failed",
                    store=store_name,
                    key=key,
                    status_code=response.status_code
                )
                return None

        except httpx.RequestError as e:
            logger.error("dapr_state_error", store=store_name, key=key, error=str(e))
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Save state to Dapr State Store.

        Args:
            store_name: Name of state store component
            key: State key
            value: State value
            ttl_seconds: Optional TTL in seconds

        Returns:
            True if saved successfully
        """
        client = await self._get_client()
        url = f"/v1.0/state/{store_name}"

        state_item = {
            "key": key,
            "value": value
        }

        if ttl_seconds:
            state_item["metadata"] = {"ttlInSeconds": str(ttl_seconds)}

        try:
            response = await client.post(url, json=[state_item])

            if response.status_code in (200, 204):
                logger.debug("state_saved", store=store_name, key=key)
                return True
            else:
                logger.error(
                    "state_save_failed",
                    store=store_name,
                    key=key,
                    status_code=response.status_code
                )
                return False

        except httpx.RequestError as e:
            logger.error("dapr_state_error", store=store_name, key=key, error=str(e))
            return False

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[dict] = None,
        http_method: str = "POST"
    ) -> Optional[dict]:
        """
        Invoke another service via Dapr Service Invocation.

        Args:
            app_id: Target service app ID (e.g., "chat-backend")
            method: Method/endpoint to invoke (e.g., "api/internal/tasks")
            data: Request body
            http_method: HTTP method (GET, POST, PUT, DELETE)

        Returns:
            Response data or None on failure
        """
        client = await self._get_client()
        url = f"/v1.0/invoke/{app_id}/method/{method}"

        try:
            if http_method.upper() == "GET":
                response = await client.get(url)
            elif http_method.upper() == "POST":
                response = await client.post(url, json=data or {})
            elif http_method.upper() == "PUT":
                response = await client.put(url, json=data or {})
            elif http_method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {http_method}")

            if response.status_code in (200, 201, 204):
                logger.info(
                    "service_invoked",
                    app_id=app_id,
                    method=method,
                    status_code=response.status_code
                )
                if response.status_code == 204:
                    return {}
                return response.json()
            else:
                logger.error(
                    "service_invocation_failed",
                    app_id=app_id,
                    method=method,
                    status_code=response.status_code,
                    response=response.text
                )
                return None

        except httpx.RequestError as e:
            logger.error(
                "dapr_invoke_error",
                app_id=app_id,
                method=method,
                error=str(e)
            )
            return None


# Singleton instance
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get singleton Dapr client instance."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
