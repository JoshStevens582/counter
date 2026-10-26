import json
from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from counter.api.deps import AskRateLimit
from counter.schemas.chat import ChatRequest
from counter.services.rag import CounterChatService

router = APIRouter(prefix="/api", tags=["chat"])


def get_chat(request: Request) -> CounterChatService:
    service = request.app.state.chat_service
    if not isinstance(service, CounterChatService):
        raise RuntimeError("Chat service is not configured.")
    return service


def require_openai_key(request: Request) -> None:
    if not request.app.state.settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not set. Add it to your environment or a .env file.",
        )


@router.post("/chat/stream")
async def ask_stream(
    payload: ChatRequest,
    request: Request,
    chat: Annotated[CounterChatService, Depends(get_chat)],
    _: Annotated[None, Depends(require_openai_key)],
    __: AskRateLimit,
) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        try:
            async for event in chat.run_ask(payload.message, payload.history):
                if await request.is_disconnected():
                    break
                yield _sse(event)
        except ValueError as exc:
            yield _sse({"type": "error", "detail": str(exc)})
        except Exception:
            yield _sse({"type": "error", "detail": "Answer generation failed."})

    return StreamingResponse(events(), media_type="text/event-stream")


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event)}\n\n"
