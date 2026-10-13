import json

import numpy as np

from ..config import EMBEDDING_DIM, VECTOR_PATH, ensure_dirs


class VectorStore:
    def __init__(self) -> None:
        ensure_dirs()
        self.vector_ids: list[str] = []
        self.vectors = np.zeros((0, EMBEDDING_DIM), dtype="float32")
        self._load()

    def add(self, vector_ids: list[str], vectors: np.ndarray) -> None:
        if len(vector_ids) == 0:
            return
        self.vector_ids.extend(vector_ids)
        self.vectors = np.vstack([self.vectors, vectors.astype("float32")])
        self._save()

    def delete(self, deleted_ids: set[str]) -> None:
        keep = [idx for idx, vector_id in enumerate(self.vector_ids) if vector_id not in deleted_ids]
        self.vector_ids = [self.vector_ids[idx] for idx in keep]
        self.vectors = self.vectors[keep] if len(keep) else np.zeros((0, EMBEDDING_DIM), dtype="float32")
        self._save()

    def search(self, query: np.ndarray, top_k: int, allowed_ids: set[str]) -> list[tuple[str, float]]:
        if self.vectors.size == 0 or not allowed_ids:
            return []
        faiss_results = self._search_with_faiss(query, top_k, allowed_ids)
        if faiss_results is not None:
            return faiss_results
        scores = self.vectors @ query.astype("float32")
        order = np.argsort(-scores)
        results: list[tuple[str, float]] = []
        for idx in order:
            vector_id = self.vector_ids[int(idx)]
            if vector_id in allowed_ids:
                results.append((vector_id, float(scores[int(idx)])))
            if len(results) >= top_k:
                break
        return results

    def _search_with_faiss(
        self, query: np.ndarray, top_k: int, allowed_ids: set[str]
    ) -> list[tuple[str, float]] | None:
        try:
            import faiss
        except Exception:
            return None

        allowed_indices = [idx for idx, vector_id in enumerate(self.vector_ids) if vector_id in allowed_ids]
        if not allowed_indices:
            return []
        vectors = self.vectors[allowed_indices].astype("float32")
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        scores, indices = index.search(query.astype("float32").reshape(1, -1), min(top_k, len(allowed_indices)))
        results: list[tuple[str, float]] = []
        for score, local_idx in zip(scores[0], indices[0]):
            if local_idx < 0:
                continue
            original_idx = allowed_indices[int(local_idx)]
            results.append((self.vector_ids[original_idx], float(score)))
        return results

    def _load(self) -> None:
        if not VECTOR_PATH.exists():
            return
        data = np.load(VECTOR_PATH, allow_pickle=False)
        self.vectors = data["vectors"].astype("float32")
        self.vector_ids = json.loads(data["vector_ids"].item())

    def _save(self) -> None:
        np.savez_compressed(VECTOR_PATH, vectors=self.vectors, vector_ids=np.array(json.dumps(self.vector_ids)))


def get_vector_store() -> VectorStore:
    return VectorStore()
