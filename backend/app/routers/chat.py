import json
import re

from fastapi import APIRouter, HTTPException

from ..config import TOP_K
from ..db import connect, rows_to_dicts, utcnow
from ..schemas import ChatRequest, ChatResponse
from ..services.llm_provider import get_llm_provider
from ..services.prompts import build_rag_prompt
from ..services.retriever import retrieve

router = APIRouter(tags=["chat"])


@router.post("/notebooks/{notebook_id}/chat", response_model=ChatResponse)
def chat(notebook_id: int, payload: ChatRequest):
    with connect() as conn:
        notebook = conn.execute("SELECT id FROM notebooks WHERE id = ?", (notebook_id,)).fetchone()
    if notebook is None:
        raise HTTPException(status_code=404, detail="Notebook not found")

    chunks = retrieve(notebook_id, payload.question, payload.top_k or TOP_K)
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages(notebook_id, role, content, citations_json, created_at) VALUES (?, 'user', ?, NULL, ?)",
            (notebook_id, payload.question, utcnow()),
        )

    if not chunks:
        answer = "Khong tim thay thong tin lien quan trong cac nguon dang bat."
        citations = []
    else:
        answer = get_llm_provider().generate(build_rag_prompt(payload.question, chunks))
        cited_ids = parse_cited_chunk_ids(answer) or {chunk["id"] for chunk in chunks[:3]}
        citations = [citation_for(chunk) for chunk in chunks if chunk["id"] in cited_ids]

    with connect() as conn:
        conn.execute(
            "INSERT INTO messages(notebook_id, role, content, citations_json, created_at) VALUES (?, 'assistant', ?, ?, ?)",
            (notebook_id, answer, json.dumps(citations), utcnow()),
        )
    return {"answer": answer, "citations": citations}


@router.get("/notebooks/{notebook_id}/messages")
def list_messages(notebook_id: int):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE notebook_id = ? ORDER BY id ASC",
            (notebook_id,),
        ).fetchall()
    return rows_to_dicts(rows)


def parse_cited_chunk_ids(answer: str) -> set[int]:
    return {int(match) for match in re.findall(r"\[chunk:(\d+)\]", answer)}


def citation_for(chunk: dict) -> dict:
    return {
        "chunk_id": chunk["id"],
        "source_id": chunk["source_id"],
        "source_title": chunk["source_title"],
        "page": chunk["page"],
        "quote": chunk["text"][:360],
    }
