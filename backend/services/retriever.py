"""
Vector store retriever configuration.
"""

from langchain_pinecone import PineconeVectorStore
from backend.core.config import settings


def get_retriever(vectorstore: PineconeVectorStore):
    """
    Wrap a Pinecone vector store as an MMR retriever.

    MMR (Maximal Marginal Relevance) balances relevance with diversity,
    reducing the chance of returning near-duplicate chunks.
    """
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.RETRIEVER_K,
            "fetch_k": settings.RETRIEVER_FETCH_K,
            "lambda_mult": settings.RETRIEVER_LAMBDA_MULT,
        },
    )
