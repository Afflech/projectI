from ..db import connect
from .embedder import get_embedder
from .vector_store import get_vector_store


def retrieve(notebook_id: int, question: str, top_k: int) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT c.vector_id
            FROM chunks c
            JOIN sources s ON s.id = c.source_id
            WHERE s.notebook_id = ? AND s.enabled = 1 AND s.status = 'ready'
            """,
            (notebook_id,),
        ).fetchall()
    allowed_ids = {row["vector_id"] for row in rows}
    query = get_embedder().embed_query(question)
    matches = get_vector_store().search(query, top_k, allowed_ids)
    if not matches:
        return []

    vector_ids = [match[0] for match in matches]
    placeholders = ",".join("?" for _ in vector_ids)
    with connect() as conn:
        chunk_rows = conn.execute(
            f"""
            SELECT c.id, c.source_id, c.page, c.text, c.vector_id, s.title AS source_title
            FROM chunks c
            JOIN sources s ON s.id = c.source_id
            WHERE c.vector_id IN ({placeholders})
            """,
            vector_ids,
        ).fetchall()
    by_vector_id = {row["vector_id"]: dict(row) for row in chunk_rows}
    ordered = []
    for vector_id, score in matches:
        if vector_id in by_vector_id:
            item = by_vector_id[vector_id]
            item["score"] = score
            ordered.append(item)
    return ordered
