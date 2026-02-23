"""
POST /ask — answers a question using the session's retriever.
"""

import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.session_store import session_store
from backend.services.rag_chain import ask

logger = logging.getLogger(__name__)
router = APIRouter()


class AskRequest(BaseModel):
    session_id: str
    question: str
    openai_key: str = ""


class AskResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    """
    Answer a natural language question using the retriever
    associated with the given session_id.
    """
    session = session_store.get(body.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a PDF first.",
        )

    effective_key = body.openai_key or session["openai_key"]

    try:
        logger.info("Running RAG chain for session: %s", body.session_id)
        answer = ask(
            retriever=session["retriever"],
            question=body.question,
            openai_key=effective_key,
        )
    except Exception:
        logger.error("RAG chain error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    return AskResponse(answer=answer, session_id=body.session_id)
