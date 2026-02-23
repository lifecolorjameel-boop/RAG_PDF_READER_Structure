"""
Embedding model setup.
Centralizing this makes it easy to swap providers (OpenAI → Cohere, etc.).
"""

from langchain_openai import OpenAIEmbeddings
from backend.core.config import settings


def get_embeddings(openai_key: str) -> OpenAIEmbeddings:
    """Return a configured OpenAI embedding model."""
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=openai_key,
    )
