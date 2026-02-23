"""
Streamlit frontend for the HR Policy Assistant.
Run with: streamlit run frontend/app.py
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


# ── Page setup ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="📄 HR Policy Assistant",
    page_icon="📄",
    layout="centered",
)
st.title("📄 HR Policy Assistant")
st.markdown("Upload your **Employee Handbook** and ask anything about company policies.")


# ── Session state defaults ─────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── Sidebar: configuration & upload ───────────────────────────────────────────

def handle_upload(openai_key, pinecone_key, index_name, uploaded_file):
    if not all([openai_key, pinecone_key, index_name, uploaded_file]):
        st.sidebar.error("Please fill in all fields and upload a PDF.")
        return

    with st.spinner("📚 Uploading and indexing PDF…"):
        try:
            response = requests.post(
                f"{API_BASE}/upload",
                data={
                    "openai_key":   openai_key,
                    "pinecone_key": pinecone_key,
                    "index_name":   index_name,
                },
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            st.session_state.session_id = data["session_id"]
            st.session_state.openai_key = openai_key
            st.session_state.chat_history = []  # Reset chat on new upload

            st.sidebar.success(
                f"✅ {data['chunks_indexed']} chunks indexed!\n\n"
                f"Session: `{data['session_id'][:8]}…`"
            )
        except requests.exceptions.RequestException as exc:
            st.sidebar.error(f"Upload failed: {exc}")


with st.sidebar:
    st.header("⚙️ Configuration")

    openai_key   = st.text_input("OpenAI API Key",     type="password", value=os.getenv("OPENAI_API_KEY", ""))
    pinecone_key = st.text_input("Pinecone API Key",   type="password", value=os.getenv("PINECONE_API_KEY", ""))
    index_name   = st.text_input("Pinecone Index Name",                 value=os.getenv("PINECONE_INDEX_NAME", ""))

    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload Employee Handbook (PDF)", type="pdf")
    upload_btn    = st.button("📤 Upload & Index PDF", use_container_width=True)

    if upload_btn:
        handle_upload(openai_key, pinecone_key, index_name, uploaded_file)


# ── Chat interface ─────────────────────────────────────────────────────────────

def fetch_answer(question: str) -> str:
    try:
        response = requests.post(
            f"{API_BASE}/ask",
            json={
                "session_id": st.session_state.session_id,
                "question":   question,
                "openai_key": st.session_state.openai_key,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as exc:
        return f"❌ API error: {exc}"


def handle_question(query: str):
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            answer = fetch_answer(query)
        st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})


st.markdown("---")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask about company policies…")

if query:
    if not st.session_state.session_id:
        st.warning("⚠️ Please upload and index a PDF first using the sidebar.")
    else:
        handle_question(query)