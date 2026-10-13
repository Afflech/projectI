import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_PATH = DATA_DIR / "vectors.npz"
DB_PATH = DATA_DIR / "notebooklm.sqlite3"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", "320"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
TOP_K = int(os.getenv("TOP_K", "5"))
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
