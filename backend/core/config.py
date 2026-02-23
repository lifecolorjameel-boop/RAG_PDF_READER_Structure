"""
Central configuration for the HR Policy RAG application.
All tuneable parameters and environment variables live here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Server ────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ── Default API Keys (can be overridden per-request) ──────────────────
    OPENAI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = ""

    # ── PDF Chunking ───────────────────────────────────────────────────────
    CHUNK_SIZE: int = 250
    CHUNK_OVERLAP: int = 30
    MIN_CHUNK_LENGTH: int = 30       # Characters — shorter chunks are dropped

    # ── Retrieval ──────────────────────────────────────────────────────────
    RETRIEVER_K: int = 3             # Final chunks returned to the LLM
    RETRIEVER_FETCH_K: int = 15      # Candidates before MMR re-ranking
    RETRIEVER_LAMBDA_MULT: float = 0.85  # 1.0 = pure relevance, 0.0 = pure diversity

    # ── LLM ───────────────────────────────────────────────────────────────
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 120
    LLM_TEMPERATURE: float = 0.0
    LLM_FREQUENCY_PENALTY: float = 0.5
    LLM_PRESENCE_PENALTY: float = 0.3
    LLM_MAX_ANSWER_SENTENCES: int = 3

    # ── Embeddings ────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"


settings = Settings()
