import os
import sys
import tempfile
from pathlib import Path


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_root))
    os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="mini-notebooklm-smoke-"))

    from app.config import UPLOAD_DIR
    from app.db import connect, init_db, utcnow
    from app.routers.chat import chat
    from app.routers.chunks import get_chunk
    from app.schemas import ChatRequest
    from app.services.ingest import ingest_source, sha256_bytes
    from app.services.retriever import retrieve

    init_db()
    text = (
        "Mini NotebookLM uses retrieval augmented generation. "
        "Citations point to source chunks. "
        "Students can ask questions about course documents."
    )
    data = text.encode("utf-8")
    file_hash = sha256_bytes(data)
    path = UPLOAD_DIR / f"{file_hash}.txt"
    path.write_bytes(data)

    with connect() as conn:
        notebook_id = conn.execute(
            "INSERT INTO notebooks(name, created_at) VALUES (?, ?)",
            ("Smoke Notebook", utcnow()),
        ).lastrowid
        source_id = conn.execute(
            """
            INSERT INTO sources(notebook_id, type, title, file_hash, status, enabled, path, created_at)
            VALUES (?, 'text', ?, ?, 'pending', 1, ?, ?)
            """,
            (notebook_id, "Smoke Source", file_hash, str(path), utcnow()),
        ).lastrowid

    ingest_source(source_id)
    chunks = retrieve(notebook_id, "What does Mini NotebookLM use?", 5)
    assert chunks, "retrieval returned no chunks"

    response = chat(notebook_id, ChatRequest(question="What does Mini NotebookLM use?"))
    assert response["citations"], "chat returned no citations"

    chunk = get_chunk(response["citations"][0]["chunk_id"])
    assert chunk["text"] == text, "citation chunk text mismatch"

    with connect() as conn:
        conn.execute("UPDATE sources SET enabled = 0 WHERE id = ?", (source_id,))
    disabled_chunks = retrieve(notebook_id, "What does Mini NotebookLM use?", 5)
    assert disabled_chunks == [], "disabled source should not be retrieved"
    disabled_response = chat(notebook_id, ChatRequest(question="What does Mini NotebookLM use?"))
    assert disabled_response["citations"] == [], "disabled source chat should not cite chunks"

    with connect() as conn:
        messages = conn.execute(
            "SELECT role FROM messages WHERE notebook_id = ? ORDER BY id",
            (notebook_id,),
        ).fetchall()
    assert [row["role"] for row in messages] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ], "chat history mismatch"

    print("Smoke test passed")
    print(f"DATA_DIR={os.environ['DATA_DIR']}")


if __name__ == "__main__":
    main()
