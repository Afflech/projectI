import re


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_tokens: int = 320, overlap: int = 64) -> list[str]:
    words = re.findall(r"\S+", normalize_text(text))
    if not words:
        return []
    if overlap >= chunk_tokens:
        overlap = max(0, chunk_tokens // 5)

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_tokens)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks
