# Mini NotebookLM

Mini NotebookLM is a Project I web app for source-grounded study Q&A. Users create notebooks, add PDF/TXT/MD or pasted text sources, then chat against enabled sources with citations back to original chunks.

## Stack

- Backend: FastAPI, SQLite, local hash embeddings for MVP, Gemini provider abstraction
- Frontend: React + Vite
- Retrieval: chunking with overlap, FAISS search when available, NumPy cosine fallback

## Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL and use `http://localhost:8000` as the API base. Without `GEMINI_API_KEY`, the backend returns retrieval-preview answers with citations, so the demo can still exercise notebook, source, chunking, retrieval, and citation flows.

## MVP Features

- Create, rename, delete notebooks
- Upload PDF/TXT/MD and paste text sources
- Background ingestion with text extraction, chunking, embeddings, and vector storage
- Enable or disable individual sources before chat
- Chat history per notebook
- Citation detail endpoint and UI panel
- Source summary and suggested questions hook

## Project Tracking

- Design notes: `docs/design.md`
- Roadmap and progress framework: `docs/project-roadmap.md`
