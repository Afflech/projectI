SYSTEM_PROMPT = """You are Mini NotebookLM, a grounded study assistant.
Answer only from the provided source chunks. If the answer is not in the chunks,
say that the sources do not contain enough information. Cite relevant chunks
using bracket markers like [chunk:123]. Keep the answer concise and useful."""


def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[chunk:{chunk['id']}] Source: {chunk['source_title']} Page: {chunk.get('page') or 'n/a'}\n{chunk['text']}"
        for chunk in chunks
    )
    return f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
