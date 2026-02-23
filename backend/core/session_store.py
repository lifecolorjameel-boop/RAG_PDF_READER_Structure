"""
In-memory session store for active RAG retriever sessions.

Each session maps a UUID to its retriever and associated metadata.
For production use, replace with Redis or a database-backed store.
"""

from typing import Any


class SessionStore:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def create(self, session_id: str, retriever: Any, openai_key: str) -> None:
        self._store[session_id] = {
            "retriever": retriever,
            "openai_key": openai_key,
        }

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._store.get(session_id)

    def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def __len__(self) -> int:
        return len(self._store)


# Singleton instance shared across the app
session_store = SessionStore()
