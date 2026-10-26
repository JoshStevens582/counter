import asyncio
from collections.abc import AsyncIterator
from typing import Any, cast

from openai import AsyncOpenAI
from openai.types.responses import EasyInputMessageParam
from openai.types.responses.response_input_param import ResponseInputParam

from counter.config import Settings
from counter.repositories.chroma_repo import ChromaChunkStore
from counter.schemas.chat import HistoryMessage, RetrievedChunk
from counter.services.citations import assign_cite_numbers, mark_cited_chunks
from counter.services.embeddings import EmbeddingClient
from counter.services.hybrid import bm25_rank, fuse_hybrid
from counter.services.openai_model_params import responses_api_kwargs
from counter.services.prompting import (
    DEVELOPER_INSTRUCTIONS,
    build_user_payload,
    keep_close_chunks,
)

NO_ANSWER_TEXT = "I could not generate an answer from the approved pages."


class CounterChatService:
    def __init__(
        self,
        settings: Settings,
        openai_client: AsyncOpenAI,
        chunk_store: ChromaChunkStore,
        embeddings: EmbeddingClient,
    ) -> None:
        self._settings = settings
        self._openai = openai_client
        self._chunk_store = chunk_store
        self._embeddings = embeddings

    async def retrieve(self, question: str) -> list[RetrievedChunk]:
        query_vector = await self._embeddings.embed_query(question)
        raw_hits = await asyncio.to_thread(
            self._chunk_store.query,
            query_vector,
            self._settings.retrieve_k,
        )
        vector_hits = keep_close_chunks(raw_hits, self._settings.max_distance)
        if not self._settings.hybrid_search_enabled:
            return vector_hits
        corpus = await asyncio.to_thread(self._chunk_store.list_chunks)
        lexical_hits = await asyncio.to_thread(
            bm25_rank,
            question,
            corpus,
            self._settings.retrieve_k,
        )
        return fuse_hybrid(
            vector_hits,
            lexical_hits,
            limit=self._settings.retrieve_k,
            rrf_k=self._settings.hybrid_rrf_k,
        )

    async def run_ask(
        self,
        question: str,
        history: list[HistoryMessage],
    ) -> AsyncIterator[dict[str, Any]]:
        cleaned = question.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty.")

        trimmed_history = _trim_history(history, self._settings.history_window)
        sources = assign_cite_numbers(await self.retrieve(cleaned))
        yield {
            "type": "sources",
            "sources": [chunk.model_dump() for chunk in sources],
        }

        prompt_messages: list[EasyInputMessageParam] = _history_as_input(trimmed_history)
        prompt_messages.append(
            {
                "role": "user",
                "content": build_user_payload(cleaned, sources),
            }
        )

        answer = ""
        async for token in self._stream_answer(prompt_messages):
            answer += token
            yield {"type": "token", "text": token}

        answer = answer.strip()
        if not answer:
            answer = NO_ANSWER_TEXT
            yield {"type": "token", "text": answer}

        sources = mark_cited_chunks(sources, answer)
        yield {
            "type": "sources",
            "sources": [chunk.model_dump() for chunk in sources],
        }
        yield {"type": "done", "answer": answer}

    async def _stream_answer(
        self,
        prompt_messages: list[EasyInputMessageParam],
    ) -> AsyncIterator[str]:
        stream_cm = self._openai.responses.stream(
            model=self._settings.openai_chat_model,
            instructions=DEVELOPER_INSTRUCTIONS,
            **responses_api_kwargs(self._settings.openai_chat_model),
            input=cast(ResponseInputParam, prompt_messages),
        )
        async with stream_cm as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta


def _history_as_input(history: list[HistoryMessage]) -> list[EasyInputMessageParam]:
    messages: list[EasyInputMessageParam] = []
    for item in history:
        messages.append({"role": item.role, "content": item.content})
    return messages


def _trim_history(
    history: list[HistoryMessage],
    window: int,
) -> list[HistoryMessage]:
    if window < 1:
        return []
    if len(history) <= window:
        return history
    return history[-window:]
