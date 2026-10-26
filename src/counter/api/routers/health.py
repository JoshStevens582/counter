import asyncio
import logging
from typing import Literal

from fastapi import APIRouter, Request, Response

from counter.repositories.chroma_repo import ChromaChunkStore
from counter.schemas.chat import HealthOut, LiveOut, ReadyOut
from counter.services.ingest import PageIngestService

router = APIRouter(prefix="/api", tags=["health"])
logger = logging.getLogger("counter.health")
_READY_CHECK_SECONDS = 2.0


@router.get("/live", response_model=LiveOut)
async def live() -> LiveOut:
    return LiveOut()


@router.get("/ready", response_model=ReadyOut)
async def ready(request: Request, response: Response) -> ReadyOut:
    chunk_store: ChromaChunkStore = request.app.state.chunk_store
    settings = request.app.state.settings
    indexed: Literal["ok", "empty"] = (
        "ok" if chunk_store.count() > 0 else "empty"
    )
    redis_ok = await _redis_status(
        getattr(request.app.state, "redis_client", None),
        required=settings.redis_required,
    )
    ok = indexed == "ok" and redis_ok
    payload = ReadyOut(
        status="ok" if ok else "unavailable",
        indexed=indexed,
    )
    if payload.status != "ok":
        response.status_code = 503
    return payload


async def _redis_status(client: object | None, *, required: bool) -> bool:
    if not required:
        return True
    if client is None:
        return False
    ping = getattr(client, "ping", None)
    if ping is None:
        return False
    try:
        replied = await asyncio.wait_for(ping(), timeout=_READY_CHECK_SECONDS)
    except Exception as exc:
        logger.warning("Readiness Redis check failed (%s).", exc)
        return False
    return bool(replied)


@router.get("/health", response_model=HealthOut)
async def health(request: Request) -> HealthOut:
    chunk_store: ChromaChunkStore = request.app.state.chunk_store
    ingest: PageIngestService = request.app.state.ingest_service
    page_count = ingest.page_file_count()
    return HealthOut(
        status="ok",
        openai_configured=bool(request.app.state.settings.openai_api_key),
        vector_store="chromadb",
        page_count=page_count,
        chunk_count=chunk_store.count(),
    )
