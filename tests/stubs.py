from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import SimpleNamespace
from typing import Any

from counter.repositories.chroma_repo import ChromaChunkStore
from counter.schemas.chat import RetrievedChunk
from counter.services.embeddings import EmbeddingClient
from counter.services.rag import CounterChatService


class StubStream:
    def __init__(self, parts: list[str]) -> None:
        self._parts = parts

    async def __aenter__(self) -> StubStream:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        return None

    def __aiter__(self) -> AsyncIterator[Any]:
        return self._events()

    async def _events(self) -> AsyncIterator[Any]:
        for part in self._parts:
            yield SimpleNamespace(type="response.output_text.delta", delta=part)

    async def get_final_response(self) -> Any:
        return SimpleNamespace(id="resp-test", output=[])


class StubOpenAI:
    def __init__(self, parts: list[str]) -> None:
        self._parts = parts
        self.responses = self
        self.stream_calls: list[dict[str, Any]] = []

    def stream(self, **kwargs: Any) -> StubStream:
        self.stream_calls.append(kwargs)
        return StubStream(self._parts)


class FakeChunkStore:
    def query(self, embedding: Sequence[float], limit: int) -> list[RetrievedChunk]:
        return []

    def list_chunks(self) -> list[RetrievedChunk]:
        return []


class FakeEmbeddings:
    async def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def fees_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        document_id="fees",
        document_title="Session fees",
        chunk_index=0,
        text="Cape Town Physio charges R650 for a standard session.",
        distance=0.2,
    )


def hours_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        document_id="hours",
        document_title="Opening hours",
        chunk_index=0,
        text="We close at 5:00 PM on weekdays.",
        distance=0.2,
    )


def services_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        document_id="services",
        document_title="What we offer",
        chunk_index=0,
        text="Sports injury assessment and rehabilitation.",
        distance=0.3,
    )


def cast_store(store: FakeChunkStore) -> ChromaChunkStore:
    return store  # type: ignore[return-value]


def cast_embeddings(embeddings: FakeEmbeddings) -> EmbeddingClient:
    return embeddings  # type: ignore[return-value]


async def collect_ask(
    service: CounterChatService,
    question: str,
) -> list[dict[str, Any]]:
    return [event async for event in service.run_ask(question, [])]
