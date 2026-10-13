import hashlib
import math
from functools import lru_cache

import numpy as np

from ..config import EMBEDDING_DIM


class Embedder:
    def __init__(self, dim: int = EMBEDDING_DIM) -> None:
        self.dim = dim

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return self._embed([f"passage: {text}" for text in texts])

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed([f"query: {text}"])[0]

    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.array([hash_embedding(text, self.dim) for text in texts], dtype="float32")
        return l2_normalize(vectors)


def hash_embedding(text: str, dim: int) -> np.ndarray:
    vector = np.zeros(dim, dtype="float32")
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = math.sqrt(float(np.dot(vector, vector)))
    if norm:
        vector /= norm
    return vector


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vectors / norms).astype("float32")


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
