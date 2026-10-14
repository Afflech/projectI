# MVP Smoke Test

Use this checklist after each meaningful backend/frontend change.

## Automated Backend Smoke

```bash
cd backend
.venv/bin/python scripts/smoke_test.py
```

Expected result:

```text
Smoke test passed
```

This verifies:

- SQLite schema initialization.
- Source ingestion from text.
- Source ingestion from a text PDF.
- PDF chunk page metadata.
- Chunk creation and vector retrieval.
- Chat response with citations.
- PDF chat citations include page metadata.
- Citation chunk lookup.
- Disabled sources are excluded from retrieval and chat citations.
- Chat history persistence.

## Frontend Build

```bash
cd frontend
npm run build
```

Expected result: Vite build completes without errors.

## Manual Demo Flow

1. Start backend with `uvicorn app.main:app --reload --port 8000`.
2. Start frontend with `npm run dev`.
3. Create a notebook.
4. Upload `demo_sources/project_i_rag_notes.pdf` and wait for `ready`.
5. Upload `demo_sources/demo-study-notes.md`.
6. Paste `demo_sources/pasted-text-sample.txt` and wait for `ready`.
7. Ask a question whose answer is in the PDF.
8. Click a PDF citation and confirm the evidence panel shows the page number.
9. Disable the pasted source and ask a question that only it can answer.
10. Refresh the page and confirm notebook/messages still load.
