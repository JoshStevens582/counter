from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from counter.api.routers.chat import router as chat_router
from counter.config import Settings
from counter.services.rag import CounterChatService


class ScriptedChat(CounterChatService):
    async def run_ask(
        self,
        question: str,
        history: list[Any],
    ) -> AsyncIterator[dict[str, Any]]:
        yield {"type": "done", "answer": "ok"}


def _app(openai_configured: bool) -> FastAPI:
    settings = Settings(
        openai_api_key="sk-test" if openai_configured else "",
        rate_limit_enabled=False,
    )
    app = FastAPI()
    app.state.settings = settings
    app.state.chat_service = ScriptedChat(
        settings,
        object(),  # type: ignore[arg-type]
        object(),  # type: ignore[arg-type]
        object(),  # type: ignore[arg-type]
    )
    app.include_router(chat_router)
    return app


@pytest.mark.asyncio
async def test_chat_stream_503_without_openai_key() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=_app(openai_configured=False)),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/chat/stream",
            json={"message": "Hi", "history": []},
        )
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_chat_stream_422_empty_message() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=_app(openai_configured=True)),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/chat/stream",
            json={"message": "", "history": []},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_stream_422_too_many_history_messages() -> None:
    history = [{"role": "user", "content": f"msg {index}"} for index in range(25)]
    async with AsyncClient(
        transport=ASGITransport(app=_app(openai_configured=True)),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/chat/stream",
            json={"message": "Hi", "history": history},
        )
    assert response.status_code == 422
