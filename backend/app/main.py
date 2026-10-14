from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGIN_REGEX, CORS_ORIGINS, ensure_dirs
from .db import init_db
from .routers import chat, chunks, notebooks, sources


def create_app() -> FastAPI:
    ensure_dirs()
    init_db()
    app = FastAPI(title="Mini NotebookLM API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_origin_regex=CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(notebooks.router)
    app.include_router(sources.router)
    app.include_router(chat.router)
    app.include_router(chunks.router)

    @app.get("/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
