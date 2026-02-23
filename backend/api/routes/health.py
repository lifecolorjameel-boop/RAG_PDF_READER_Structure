"""
Health check endpoint.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Returns 200 OK when the service is running."""
    return {"status": "ok"}
