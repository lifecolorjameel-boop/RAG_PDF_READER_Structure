"""
POST /upload — accepts a PDF, indexes it into Pinecone, and returns a session_id.
"""

import os
import uuid
import logging
import tempfile
import traceback

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.core.session_store import session_store
from backend.services.indexer import index_pdf
from backend.services.retriever import get_retriever

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    session_id: str
    chunks_indexed: int
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    openai_key: str  = Form(...),
    pinecone_key: str = Form(...),
    index_name: str  = Form(...),
):
    """
    Upload a PDF, embed its chunks into Pinecone, and return a session_id
    that the client must pass to /ask.
    """
    _validate_pdf(file)

    tmp_path = await _save_to_temp(file)

    try:
        logger.info("Indexing PDF: %s", file.filename)
        vectorstore, num_chunks = index_pdf(
            tmp_path=tmp_path,
            openai_key=openai_key,
            pinecone_key=pinecone_key,
            index_name=index_name,
        )
        logger.info("Indexed %d chunks.", num_chunks)
    except Exception:
        logger.error("Indexing failed:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="PDF indexing failed. Check your API keys and index name.")
    finally:
        _cleanup(tmp_path)

    session_id = str(uuid.uuid4())
    session_store.create(
        session_id=session_id,
        retriever=get_retriever(vectorstore),
        openai_key=openai_key,
    )

    return UploadResponse(
        session_id=session_id,
        chunks_indexed=num_chunks,
        message=f"Successfully indexed {num_chunks} chunks.",
    )


# ── Private helpers ────────────────────────────────────────────────────────────

def _validate_pdf(file: UploadFile) -> None:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")


async def _save_to_temp(file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        return tmp.name


def _cleanup(path: str) -> None:
    if os.path.exists(path):
        os.unlink(path)
