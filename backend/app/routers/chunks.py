from fastapi import APIRouter, HTTPException

from ..db import connect, row_to_dict

router = APIRouter(prefix="/chunks", tags=["chunks"])


@router.get("/{chunk_id}")
def get_chunk(chunk_id: int):
    with connect() as conn:
        row = conn.execute(
            """
            SELECT c.id, c.source_id, c.page, c.text, s.title AS source_title
            FROM chunks c
            JOIN sources s ON s.id = c.source_id
            WHERE c.id = ?
            """,
            (chunk_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return row_to_dict(row)
