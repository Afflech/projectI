from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class NotebookUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class TextSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    text: str = Field(min_length=1)


class SourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    enabled: bool | None = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=12)


class Citation(BaseModel):
    chunk_id: int
    source_id: int
    source_title: str
    page: int | None = None
    quote: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
