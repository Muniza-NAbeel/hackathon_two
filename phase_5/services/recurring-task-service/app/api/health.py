"""Health Check Endpoints for Recurring Task Service"""
from fastapi import APIRouter
import os

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Liveness probe endpoint."""
    return {
        "status": "healthy",
        "service": "recurring-task-service",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe endpoint."""
    import httpx

    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    dapr_url = f"http://localhost:{dapr_port}/v1.0/healthz"

    ready = True
    dapr_status = "unknown"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(dapr_url, timeout=2.0)
            dapr_status = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        dapr_status = f"error: {str(e)}"

    return {
        "ready": ready,
        "service": "recurring-task-service",
        "dapr": dapr_status
    }
