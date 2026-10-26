import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from counter.api.routers.chat import router as chat_router
from counter.api.routers.health import router as health_router
from counter.config import UNSET_OPENAI_API_KEY_PLACEHOLDER, load_settings
from counter.repositories.chroma_repo import ChromaChunkStore
from counter.services.embeddings import EmbeddingClient
from counter.services.ingest import IngestError, PageIngestService
from counter.services.rag import CounterChatService
from counter.services.rate_limit import RateLimiter
from counter.services.redis_client import connect_redis

logger = logging.getLogger("counter.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    Path("data").mkdir(exist_ok=True)
    Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)

    openai_client = AsyncOpenAI(
        api_key=settings.openai_api_key or UNSET_OPENAI_API_KEY_PLACEHOLDER
    )
    embeddings = EmbeddingClient(openai_client, settings.openai_embedding_model)
    chunk_store = ChromaChunkStore(settings.chroma_path)
    ingest_service = PageIngestService(settings, chunk_store, embeddings)
    chat_service = CounterChatService(settings, openai_client, chunk_store, embeddings)
    redis_client = await connect_redis(settings)
    rate_limiter = (
        RateLimiter(redis_client, settings)
        if redis_client is not None and settings.rate_limit_enabled
        else None
    )

    try:
        seeded = await ingest_service.seed_pages()
        if seeded:
            logger.info("Indexed demo pages on first boot: %s", ", ".join(seeded))
    except IngestError as exc:
        logger.error("Page ingest failed: %s", exc)

    app.state.settings = settings
    app.state.chunk_store = chunk_store
    app.state.ingest_service = ingest_service
    app.state.chat_service = chat_service
    app.state.redis_client = redis_client
    app.state.rate_limiter = rate_limiter
    yield
    if redis_client is not None:
        await redis_client.aclose()


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(title="Counter", lifespan=lifespan)
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()
