"""
RAG chain: combines the retriever, prompt, and LLM into a single callable.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from backend.core.config import settings
from config.prompts import RAG_SYSTEM_PROMPT


def build_rag_chain(retriever, openai_key: str):
    """Construct and return a LangChain RAG chain."""
    llm = _build_llm(openai_key)
    prompt = ChatPromptTemplate.from_template(RAG_SYSTEM_PROMPT)

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def ask(retriever, question: str, openai_key: str) -> str:
    """
    Run the RAG chain for a single question and return a concise answer.

    Answers are trimmed to a maximum of `LLM_MAX_ANSWER_SENTENCES` sentences
    as a safety net against unexpectedly verbose LLM output.
    """
    if not question or not question.strip():
        return "Please enter a valid question."

    chain = build_rag_chain(retriever, openai_key)
    raw_answer = chain.invoke(question)
    return _trim_to_max_sentences(raw_answer, settings.LLM_MAX_ANSWER_SENTENCES)


# ── Private helpers ────────────────────────────────────────────────────────────

def _build_llm(openai_key: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=openai_key,
        max_tokens=settings.LLM_MAX_TOKENS,
        model_kwargs={
            "frequency_penalty": settings.LLM_FREQUENCY_PENALTY,
            "presence_penalty": settings.LLM_PRESENCE_PENALTY,
        },
    )


def _format_docs(docs) -> str:
    """Convert retrieved documents into a numbered context string."""
    if not docs:
        return "No relevant content found."
    return "\n\n---\n\n".join(
        f"[Page {int(doc.metadata.get('page', 0)) + 1}] {doc.page_content.strip()}"
        for doc in docs
    )


def _trim_to_max_sentences(text: str, max_sentences: int) -> str:
    """Trim an answer to at most `max_sentences` sentences."""
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    if len(sentences) <= max_sentences:
        return text.strip()
    return ". ".join(sentences[:max_sentences]) + "."
