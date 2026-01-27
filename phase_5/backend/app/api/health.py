"""
Health Check Endpoints (T152)

Provides health check endpoints for monitoring, load balancers, and K8s probes.

Endpoints:
- /health: Basic health check (for liveness probes)
- /health/deep: Deep health check with database connectivity (for readiness probes)
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from app.db.database import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint for liveness probes.

    Returns 200 OK if the service is running.
    No dependencies on external services.

    Used by:
    - Kubernetes liveness probes
    - Load balancers
    - Monitoring systems
    """
    return {
        "status": "healthy",
        "service": "phase3-backend",
        "version": "1.0.0",
    }


@router.get("/health/deep")
async def deep_health_check(db: Session = Depends(get_session)):
    """
    Deep health check endpoint for readiness probes.

    Tests:
    - Database connectivity
    - Database query execution

    Returns:
    - 200 OK if all systems operational
    - 503 Service Unavailable if any system is down

    Used by:
    - Kubernetes readiness probes
    - Pre-deployment validation
    """
    try:
        # Test database connection with a simple query
        result = db.execute(select(1)).scalar()

        if result != 1:
            raise Exception("Database query returned unexpected result")

        return {
            "status": "healthy",
            "service": "phase3-backend",
            "version": "1.0.0",
            "checks": {
                "database": "connected",
            },
        }

    except Exception as e:
        logger.error(f"Deep health check failed: {str(e)}")

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "phase3-backend",
                "version": "1.0.0",
                "checks": {
                    "database": "disconnected",
                },
                "error": str(e),
            },
        )
