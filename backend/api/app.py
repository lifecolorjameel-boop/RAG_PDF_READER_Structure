"""
FastAPI application factory.
Registers middleware and all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import health, upload, ask


def create_app() -> FastAPI:
    app = FastAPI(
        title="HR Policy RAG API",
        version="1.0.0",
        description="Upload an Employee Handbook PDF and ask natural language questions.",
    )

    _register_middleware(app)
    _register_routes(app)

    return app


def _register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routes(app: FastAPI) -> None:
    app.include_router(health.router, tags=["Health"])
    app.include_router(upload.router, tags=["Documents"])
    app.include_router(ask.router,    tags=["Q&A"])


app = create_app()
