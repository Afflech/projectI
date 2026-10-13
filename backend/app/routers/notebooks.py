from fastapi import APIRouter, HTTPException

from ..db import connect, row_to_dict, rows_to_dicts, utcnow
from ..schemas import NotebookCreate, NotebookUpdate

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("")
def list_notebooks():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM notebooks ORDER BY created_at DESC").fetchall()
    return rows_to_dicts(rows)


@router.post("")
def create_notebook(payload: NotebookCreate):
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO notebooks(name, created_at) VALUES (?, ?)",
            (payload.name.strip(), utcnow()),
        )
        row = conn.execute("SELECT * FROM notebooks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


@router.patch("/{notebook_id}")
def update_notebook(notebook_id: int, payload: NotebookUpdate):
    with connect() as conn:
        conn.execute("UPDATE notebooks SET name = ? WHERE id = ?", (payload.name.strip(), notebook_id))
        row = conn.execute("SELECT * FROM notebooks WHERE id = ?", (notebook_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return row_to_dict(row)


@router.delete("/{notebook_id}")
def delete_notebook(notebook_id: int):
    with connect() as conn:
        cursor = conn.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {"ok": True}
