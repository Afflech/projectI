import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

from ..config import CHUNK_OVERLAP, CHUNK_TOKENS
from ..db import connect
from .chunker import chunk_text, normalize_text
from .embedder import get_embedder
from .llm_provider import get_llm_provider
from .prompts import build_rag_prompt
from .vector_store import get_vector_store


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_source(source_id: int) -> None:
    with connect() as conn:
        conn.execute("UPDATE sources SET status = 'processing', error = NULL WHERE id = ?", (source_id,))
        source = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    if source is None:
        return

    try:
        pages = extract_pages(source["path"], source["type"])
        chunk_rows: list[tuple[int | None, str]] = []
        for page, text in pages:
            for chunk in chunk_text(text, CHUNK_TOKENS, CHUNK_OVERLAP):
                chunk_rows.append((page, chunk))
        if not chunk_rows:
            raise ValueError("No extractable text found in source.")

        embedder = get_embedder()
        vectors = embedder.embed_passages([row[1] for row in chunk_rows])
        vector_ids: list[str] = []
        with connect() as conn:
            old_ids = [
                row["vector_id"]
                for row in conn.execute("SELECT vector_id FROM chunks WHERE source_id = ?", (source_id,)).fetchall()
            ]
            conn.execute("DELETE FROM chunks WHERE source_id = ?", (source_id,))
            for idx, (page, text) in enumerate(chunk_rows):
                vector_id = f"source:{source_id}:chunk:{idx}"
                vector_ids.append(vector_id)
                conn.execute(
                    "INSERT INTO chunks(source_id, page, text, vector_id) VALUES (?, ?, ?, ?)",
                    (source_id, page, text, vector_id),
                )
            conn.execute("UPDATE sources SET status = 'ready' WHERE id = ?", (source_id,))
        if old_ids:
            get_vector_store().delete(set(old_ids))
        get_vector_store().add(vector_ids, vectors)
        summarize_source(source_id)
    except Exception as exc:
        with connect() as conn:
            conn.execute(
                "UPDATE sources SET status = 'failed', error = ? WHERE id = ?",
                (str(exc), source_id),
            )


def extract_pages(path: str, source_type: str) -> list[tuple[int | None, str]]:
    file_path = Path(path)
    if source_type == "pdf":
        reader = PdfReader(str(file_path))
        return [(idx, normalize_text(page.extract_text() or "")) for idx, page in enumerate(reader.pages, start=1)]
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return [(None, normalize_text(text))]


def summarize_source(source_id: int) -> None:
    with connect() as conn:
        source = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        chunks = conn.execute(
            "SELECT id, text, page FROM chunks WHERE source_id = ? ORDER BY id LIMIT 6",
            (source_id,),
        ).fetchall()
    if source is None or not chunks:
        return
    prompt_chunks = [
        {"id": row["id"], "text": row["text"], "page": row["page"], "source_title": source["title"]}
        for row in chunks
    ]
    prompt = (
        build_rag_prompt("Summarize this source in 5 bullets and suggest 5 study questions.", prompt_chunks)
        + "\nReturn Vietnamese text when possible."
    )
    try:
        text = get_llm_provider().generate(prompt)
    except Exception:
        text = "Summary is unavailable because the LLM provider failed."
    questions = [line.strip("- ").strip() for line in text.splitlines() if line.strip().endswith("?")][:5]
    with connect() as conn:
        conn.execute(
            "UPDATE sources SET summary = ?, suggested_questions_json = ? WHERE id = ?",
            (text, json.dumps(questions), source_id),
        )
