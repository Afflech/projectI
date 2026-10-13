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
- Chunk creation and vector retrieval.
- Chat response with citations.
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
4. Paste a text source and wait for `ready`.
5. Ask a question whose answer is in the source.
6. Click a citation and confirm the evidence panel shows the source text.
7. Disable the source and ask again.
8. Refresh the page and confirm notebook/messages still load.
