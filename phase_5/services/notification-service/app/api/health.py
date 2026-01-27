"""
Health Check Endpoints for Notification Service

Provides Kubernetes-compatible health and readiness probes.
"""
from fastapi import APIRouter
import os

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Liveness probe endpoint.

    Returns 200 if the service is alive.
    Used by Kubernetes to determine if the container needs restart.
    """
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe endpoint.

    Returns 200 if the service is ready to accept traffic.
    Checks Dapr sidecar availability.
    """
    import httpx

    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    dapr_url = f"http://localhost:{dapr_port}/v1.0/healthz"

    ready = True
    dapr_status = "unknown"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(dapr_url, timeout=2.0)
            if response.status_code == 200:
                dapr_status = "healthy"
            else:
                dapr_status = "unhealthy"
                ready = False
    except Exception as e:
        dapr_status = f"error: {str(e)}"
        # Don't mark as not ready if Dapr is temporarily unavailable
        # This allows the service to start before Dapr sidecar

    return {
        "ready": ready,
        "service": "notification-service",
        "dapr": dapr_status
    }
