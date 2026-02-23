"""
PDF loading, chunking, and Pinecone indexing service.
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

from backend.core.config import settings
from backend.services.embeddings import get_embeddings


def index_pdf(
    tmp_path: str,
    openai_key: str,
    pinecone_key: str,
    index_name: str,
) -> tuple[PineconeVectorStore, int]:
    """
    Load a PDF, split it into chunks, embed them, and upsert into Pinecone.

    Returns:
        (vectorstore, number_of_chunks_indexed)
    """
    os.environ["PINECONE_API_KEY"] = pinecone_key

    documents = _load_pdf(tmp_path)
    chunks = _split_documents(documents)

    embeddings = get_embeddings(openai_key)
    vectorstore = PineconeVectorStore.from_documents(
        chunks, embedding=embeddings, index_name=index_name
    )

    return vectorstore, len(chunks)


# ── Private helpers ────────────────────────────────────────────────────────────

def _load_pdf(path: str):
    """Load a PDF and filter out blank pages."""
    loader = PyPDFLoader(path)
    documents = loader.load()
    return [doc for doc in documents if doc.page_content.strip()]


def _split_documents(documents):
    """Split documents into chunks and drop fragments that are too short."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return [
        chunk for chunk in chunks
        if len(chunk.page_content.strip()) > settings.MIN_CHUNK_LENGTH
    ]
