from typing import Literal

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class RetrievedChunk(BaseModel):
    document_id: str
    document_title: str
    chunk_index: int
    text: str
    distance: float
    match: str = "vector"
    cite_n: int = 0
    cited: bool | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=24)


class HealthOut(BaseModel):
    status: str
    openai_configured: bool
    vector_store: str
    page_count: int
    chunk_count: int


class LiveOut(BaseModel):
    status: Literal["ok"] = "ok"


class ReadyOut(BaseModel):
    status: Literal["ok", "unavailable"]
    indexed: Literal["ok", "empty"]
