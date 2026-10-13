# Mini NotebookLM Design

## Goal

The app helps students ask questions over course material and receive answers grounded in uploaded sources.

## RAG Flow

1. Source upload or pasted text is stored with `pending` status.
2. Background ingestion extracts text, preserves PDF page numbers, chunks text with overlap, embeds chunks, and stores vectors.
3. Chat embeds the question with a `query:` prefix, retrieves top-k chunks from enabled sources, builds a grounded prompt, and calls the configured LLM provider.
4. The answer and citations are saved in notebook chat history.

## Data Model

- `notebooks`: notebook metadata
- `sources`: uploaded/pasted source metadata, status, enabled flag, summary
- `chunks`: source chunks with page and vector id
- `messages`: chat history and citation JSON
- `notes`: reserved for saved answers

## Demo Risk Controls

- If Gemini quota or key is unavailable, mock LLM mode still shows retrieved citations.
- Embeddings are local and deterministic for MVP; the embedder service can be replaced with multilingual-e5-small later.
- Ingestion status is visible in the UI.
