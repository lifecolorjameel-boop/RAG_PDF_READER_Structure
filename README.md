# 📄 HR Policy Assistant

A production-ready RAG (Retrieval-Augmented Generation) application that lets you upload an HR/Employee Handbook PDF and ask natural language questions about company policies.

Built with **FastAPI**, **Streamlit**, **LangChain**, **OpenAI**, and **Pinecone**.

---

##  Project Structure

```
hr-policy-assistant/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI app factory & middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py       # GET /health
│   │       ├── upload.py       # POST /upload
│   │       └── ask.py          # POST /ask
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings (env vars, defaults)
│   │   └── session_store.py    # In-memory session management
│   │
│   └── services/
│       ├── __init__.py
│       ├── embeddings.py       # Embedding model setup
│       ├── indexer.py          # PDF loading & chunking
│       ├── retriever.py        # Vector store retriever
│       └── rag_chain.py        # Prompt + LLM + chain
│
├── frontend/
│   └── app.py                  # Streamlit UI
│
├── config/
│   └── prompts.py              # Centralized prompt templates
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── main.py                     # Backend entry point
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd hr-policy-assistant
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 3. Run the backend

```bash
python main.py
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 4. Run the frontend (new terminal)

```bash
streamlit run frontend/app.py
# UI available at http://localhost:8501
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `PINECONE_API_KEY` | Your Pinecone API key | Yes |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | Yes |
| `API_BASE_URL` | Backend URL for the frontend | No (default: `http://localhost:8000`) |
| `API_HOST` | Host to bind the backend server | No (default: `0.0.0.0`) |
| `API_PORT` | Port for the backend server | No (default: `8000`) |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload & index a PDF |
| `POST` | `/ask` | Ask a question about the document |

### POST `/upload`
Accepts `multipart/form-data`:
- `file` — PDF file
- `openai_key` — OpenAI API key
- `pinecone_key` — Pinecone API key
- `index_name` — Pinecone index name

### POST `/ask`
Accepts JSON:
```json
{
  "session_id": "uuid",
  "question": "How many vacation days do I get?",
  "openai_key": "sk-..."
}
```

---

## 🧱 Architecture

```
PDF Upload
    │
    ▼
PyPDFLoader → RecursiveTextSplitter → OpenAI Embeddings → Pinecone VectorStore
                                                                    │
User Question                                                       │
    │                                                               ▼
    └─────────────────────────────────────────► MMR Retriever → Top-K Chunks
                                                                    │
                                                                    ▼
                                                          ChatPromptTemplate
                                                                    │
                                                                    ▼
                                                          GPT-4o-mini → Answer
```

---

## ⚙️ Configuration Tuning

All chunking, retrieval, and model settings live in `backend/core/config.py`. Key parameters:

- `CHUNK_SIZE` — Token size per chunk (default: 250)
- `CHUNK_OVERLAP` — Overlap between chunks (default: 30)
- `RETRIEVER_K` — Number of chunks returned (default: 3)
- `RETRIEVER_FETCH_K` — Candidates before MMR reranking (default: 15)
- `LLM_MODEL` — OpenAI model name (default: `gpt-4o-mini`)
- `LLM_MAX_TOKENS` — Max tokens in response (default: 120)

---

## 📦 Tech Stack

- **FastAPI** — REST API backend
- **Streamlit** — Interactive frontend
- **LangChain** — RAG orchestration
- **OpenAI** — Embeddings (`text-embedding-3-small`) + LLM (`gpt-4o-mini`)
- **Pinecone** — Vector database
- **PyPDF** — PDF parsing
