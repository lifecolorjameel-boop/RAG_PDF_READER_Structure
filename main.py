"""
Entry point for the HR Policy RAG backend server.
Run with: python main.py
"""

import uvicorn
from backend.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
