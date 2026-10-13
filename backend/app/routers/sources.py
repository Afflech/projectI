from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from ..config import UPLOAD_DIR
from ..db import connect, remove_file, row_to_dict, rows_to_dicts, utcnow
from ..schemas import SourceUpdate, TextSourceCreate
from ..services.ingest import ingest_source, sha256_bytes
from ..services.vector_store import get_vector_store

router = APIRouter(tags=["sources"])


@router.get("/notebooks/{notebook_id}/sources")
def list_sources(notebook_id: int):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM sources WHERE notebook_id = ? ORDER BY created_at DESC",
            (notebook_id,),
        ).fetchall()
    return rows_to_dicts(rows)


@router.post("/notebooks/{notebook_id}/sources")
async def upload_source(
    notebook_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
):
    ensure_notebook(notebook_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported")
    data = await file.read()
    file_hash = sha256_bytes(data)
    source_type = suffix.removeprefix(".")
    path = UPLOAD_DIR / f"{file_hash}{suffix}"
    path.write_bytes(data)
    source_title = (title or file.filename or "Untitled source").strip()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sources(notebook_id, type, title, file_hash, status, enabled, path, created_at)
            VALUES (?, ?, ?, ?, 'pending', 1, ?, ?)
            """,
            (notebook_id, source_type, source_title, file_hash, str(path), utcnow()),
        )
        source_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    background_tasks.add_task(ingest_source, source_id)
    return row_to_dict(row)


@router.post("/notebooks/{notebook_id}/sources/text")
def create_text_source(notebook_id: int, payload: TextSourceCreate, background_tasks: BackgroundTasks):
    ensure_notebook(notebook_id)
    data = payload.text.encode("utf-8")
    file_hash = sha256_bytes(data)
    path = UPLOAD_DIR / f"{file_hash}.txt"
    path.write_bytes(data)
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sources(notebook_id, type, title, file_hash, status, enabled, path, created_at)
            VALUES (?, 'text', ?, ?, 'pending', 1, ?, ?)
            """,
            (notebook_id, payload.title.strip(), file_hash, str(path), utcnow()),
        )
        source_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    background_tasks.add_task(ingest_source, source_id)
    return row_to_dict(row)


@router.get("/sources/{source_id}/status")
def source_status(source_id: int):
    with connect() as conn:
        row = conn.execute("SELECT id, status, error FROM sources WHERE id = ?", (source_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return row_to_dict(row)


@router.patch("/sources/{source_id}")
def update_source(source_id: int, payload: SourceUpdate):
    fields = []
    values = []
    if payload.title is not None:
        fields.append("title = ?")
        values.append(payload.title.strip())
    if payload.enabled is not None:
        fields.append("enabled = ?")
        values.append(1 if payload.enabled else 0)
    if not fields:
        raise HTTPException(status_code=400, detail="No changes provided")
    values.append(source_id)
    with connect() as conn:
        conn.execute(f"UPDATE sources SET {', '.join(fields)} WHERE id = ?", values)
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return row_to_dict(row)


@router.delete("/sources/{source_id}")
def delete_source(source_id: int):
    with connect() as conn:
        row = conn.execute("SELECT path FROM sources WHERE id = ?", (source_id,)).fetchone()
        vector_rows = conn.execute("SELECT vector_id FROM chunks WHERE source_id = ?", (source_id,)).fetchall()
        cursor = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Source not found")
    get_vector_store().delete({item["vector_id"] for item in vector_rows})
    remove_file(row["path"] if row else None)
    return {"ok": True}


def ensure_notebook(notebook_id: int) -> None:
    with connect() as conn:
        row = conn.execute("SELECT id FROM notebooks WHERE id = ?", (notebook_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
