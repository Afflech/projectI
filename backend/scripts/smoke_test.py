import os
import sys
import tempfile
from pathlib import Path


def demo_pdf_bytes() -> bytes:
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 7 0 R >> >> /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 199 >>
stream
BT /F1 12 Tf 72 720 Td (Project I Mini NotebookLM Demo PDF. Page one states that retrieval augmented generation grounds answers in enabled sources. Citations must point back to source chunks.) Tj ET
endstream
endobj
5 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 7 0 R >> >> /Contents 6 0 R >>
endobj
6 0 obj
<< /Length 170 >>
stream
BT /F1 12 Tf 72 720 Td (Page two states that scanned PDFs without OCR may fail because no extractable text is available. The demo should disclose this limitation.) Tj ET
endstream
endobj
7 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 8
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000121 00000 n 
0000000247 00000 n 
0000000496 00000 n 
0000000622 00000 n 
0000000842 00000 n 
trailer
<< /Size 8 /Root 1 0 R >>
startxref
912
%%EOF
"""


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

    pdf_data = demo_pdf_bytes()
    pdf_hash = sha256_bytes(pdf_data)
    pdf_path = UPLOAD_DIR / f"{pdf_hash}.pdf"
    pdf_path.write_bytes(pdf_data)
    with connect() as conn:
        pdf_source_id = conn.execute(
            """
            INSERT INTO sources(notebook_id, type, title, file_hash, status, enabled, path, created_at)
            VALUES (?, 'pdf', ?, ?, 'pending', 1, ?, ?)
            """,
            (notebook_id, "Demo PDF", pdf_hash, str(pdf_path), utcnow()),
        ).lastrowid

    ingest_source(pdf_source_id)
    with connect() as conn:
        pdf_source = conn.execute("SELECT status, error FROM sources WHERE id = ?", (pdf_source_id,)).fetchone()
        page_rows = conn.execute(
            "SELECT page FROM chunks WHERE source_id = ? ORDER BY page",
            (pdf_source_id,),
        ).fetchall()
    assert pdf_source["status"] == "ready", f"PDF source failed: {pdf_source['error']}"
    assert [row["page"] for row in page_rows] == [1, 2], "PDF chunks should preserve page numbers"

    pdf_response = chat(
        notebook_id,
        ChatRequest(question="What limitation does page two mention about scanned PDFs?"),
    )
    assert pdf_response["citations"], "PDF chat returned no citations"
    assert any(item["page"] is not None for item in pdf_response["citations"]), "PDF citations should include page"
    pdf_chunk = get_chunk(pdf_response["citations"][0]["chunk_id"])
    assert pdf_chunk["page"] in {1, 2}, "PDF citation lookup should include source page"

    with connect() as conn:
        messages = conn.execute(
            "SELECT role FROM messages WHERE notebook_id = ? ORDER BY id",
            (notebook_id,),
        ).fetchall()
    assert [row["role"] for row in messages] == ["user", "assistant"] * 3, "chat history mismatch"

    print("Smoke test passed")
    print(f"DATA_DIR={os.environ['DATA_DIR']}")


if __name__ == "__main__":
    main()
