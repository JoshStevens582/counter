from typing import Any

import pytest

from counter.config import Settings
from counter.schemas.chat import HistoryMessage
from counter.services.rag import CounterChatService
from tests.stubs import (
    FakeChunkStore,
    FakeEmbeddings,
    StubOpenAI,
    cast_embeddings,
    cast_store,
    collect_ask,
    fees_chunk,
    hours_chunk,
    services_chunk,
)


def _service(settings: Settings, parts: list[str]) -> CounterChatService:
    return CounterChatService(
        settings,
        StubOpenAI(parts),  # type: ignore[arg-type]
        cast_store(FakeChunkStore()),
        cast_embeddings(FakeEmbeddings()),
    )


async def _with_sources(
    service: CounterChatService,
    sources: list[Any],
    question: str,
) -> list[dict[str, Any]]:
    async def fake_retrieve(_question: str) -> list[Any]:
        return sources

    service.retrieve = fake_retrieve  # type: ignore[method-assign]
    return await collect_ask(service, question)


@pytest.mark.asyncio
async def test_run_ask_fees_cites_fees_page(settings: Settings) -> None:
    service = _service(settings, ["A session costs R650 [1]."])
    events = await _with_sources(service, [fees_chunk()], "What does a session cost?")
    first_sources = events[0]["sources"]
    assert first_sources[0]["document_id"] == "fees"
    final_sources = next(e for e in events if e["type"] == "sources" and e != events[0])
    assert final_sources["sources"][0]["cited"] is True
    assert events[-1]["answer"] == "A session costs R650 [1]."


@pytest.mark.asyncio
async def test_run_ask_hours_cites_hours_page(settings: Settings) -> None:
    service = _service(settings, ["We close at 5:00 PM on weekdays [1]."])
    events = await _with_sources(service, [hours_chunk()], "What time do you close?")
    assert events[0]["sources"][0]["document_id"] == "hours"
    final = next(e for e in reversed(events) if e["type"] == "sources")
    assert final["sources"][0]["cited"] is True


@pytest.mark.asyncio
async def test_run_ask_unknown_answer(settings: Settings) -> None:
    service = _service(
        settings,
        ["I do not know that from the approved pages."],
    )
    events = await _with_sources(service, [services_chunk()], "Who is the CEO?")
    assert "do not know" in events[-1]["answer"].lower()


@pytest.mark.asyncio
async def test_run_ask_booking_refusal(settings: Settings) -> None:
    service = _service(
        settings,
        [
            "A session costs R650 [1]. Counter cannot book appointments; "
            "please contact reception during opening hours.",
        ],
    )
    events = await _with_sources(
        service,
        [fees_chunk()],
        "Book me Tuesday at 2 and what does it cost?",
    )
    answer = events[-1]["answer"].lower()
    assert "650" in answer or "r650" in answer
    assert "cannot book" in answer or "contact" in answer


@pytest.mark.asyncio
async def test_run_ask_drops_fake_citation_numbers(settings: Settings) -> None:
    service = _service(settings, ["The price is R650 [1] and also [99]."])
    events = await _with_sources(service, [fees_chunk()], "What does a session cost?")
    final = next(e for e in reversed(events) if e["type"] == "sources")
    cited = [s for s in final["sources"] if s.get("cited")]
    assert len(cited) == 1
    assert cited[0]["cite_n"] == 1


@pytest.mark.asyncio
async def test_run_ask_rejects_blank_question(settings: Settings) -> None:
    service = _service(settings, [])
    with pytest.raises(ValueError, match="empty"):
        await collect_ask(service, "   ")


@pytest.mark.asyncio
async def test_run_ask_trims_history(settings: Settings) -> None:
    service = _service(settings, ["A session costs R650 [1]."])
    long_history = [
        HistoryMessage(role="user", content=f"Turn {index}")
        for index in range(20)
    ]

    async def fake_retrieve(_question: str) -> list[Any]:
        return [fees_chunk()]

    service.retrieve = fake_retrieve  # type: ignore[method-assign]
    _ = [event async for event in service.run_ask("What does a session cost?", long_history)]
    stream_input = service._openai.stream_calls[-1]["input"]  # type: ignore[attr-defined]
    user_turns = [message for message in stream_input if message["role"] == "user"]
    assert len(user_turns) == 13
