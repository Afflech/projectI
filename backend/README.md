# Mini NotebookLM Backend

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Without `GEMINI_API_KEY`, chat uses a mock LLM answer that still returns retrieved citations.

## Core API

- `POST /notebooks`, `GET /notebooks`, `PATCH /notebooks/{id}`, `DELETE /notebooks/{id}`
- `POST /notebooks/{id}/sources` for PDF/TXT/MD uploads
- `POST /notebooks/{id}/sources/text` for pasted text
- `PATCH /sources/{id}` for enable/disable or rename
- `POST /notebooks/{id}/chat`
- `GET /chunks/{id}` for citation detail
