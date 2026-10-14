# Demo Checklist - Real Sources MVP

Use this checklist to verify the MVP with real source files before recording or
presenting the Project I demo.

## Demo Sources

Use the files in `demo_sources/`:

- `project_i_rag_notes.pdf`: two-page text PDF with extractable text and page metadata.
- `demo-study-notes.md`: short TXT/MD-style study note.
- `pasted-text-sample.txt`: paste this content through the UI as pasted text.
- `demo-questions.json`: 7 manual questions with expected source/page evidence.

Do not use sensitive personal, school, or customer documents in the demo.

## Startup

1. Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

2. Start the frontend:

```bash
cd frontend
npm run dev
```

3. Open the Vite URL in Chrome.

Without `GEMINI_API_KEY`, the mock provider is acceptable for this checklist
because retrieval, source filtering, citations, and history persistence still run.

## Browser Flow

1. Create a notebook named `Project I Demo`.
2. Rename it to `Project I Demo - Verified`.
3. Upload `demo_sources/project_i_rag_notes.pdf`.
4. Upload `demo_sources/demo-study-notes.md`.
5. Paste the contents of `demo_sources/pasted-text-sample.txt` as a source named `Demo Pasted Text`.
6. Wait until all sources show `ready`.
7. Select the PDF source and confirm the summary panel appears after processing.
8. Ask: `What limitation does page two of the PDF mention?`
9. Confirm the answer has a citation chip for the PDF with `p.2` or another visible page number.
10. Click the citation and confirm the evidence panel shows `Page 2`.
11. Ask: `Why is the offline mock provider acceptable for the MVP demo?`
12. Confirm the citation points to `Demo Pasted Text`.
13. Disable `Demo Pasted Text`.
14. Ask the same mock-provider question again.
15. Confirm the new answer no longer cites `Demo Pasted Text`.
16. Refresh the browser.
17. Confirm the notebook, sources, and chat history still load.

## Expected Error Case

If a scanned PDF or image-only PDF is uploaded, the source should move to
`failed` with `No extractable text found in source.` This is an accepted MVP
limitation unless OCR is added later.

## Automated Checks

Run the backend smoke test:

```bash
cd backend
.venv/bin/python scripts/smoke_test.py
```

Expected result:

```text
Smoke test passed
```

Run the frontend build:

```bash
cd frontend
npm run build
```

Expected result: Vite build completes without errors.
