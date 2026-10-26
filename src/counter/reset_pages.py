"""Re-index every file in pages/. Stop the API first if it is running."""

import asyncio
import logging

from openai import AsyncOpenAI

from counter.config import load_settings
from counter.repositories.chroma_repo import ChromaChunkStore
from counter.services.embeddings import EmbeddingClient
from counter.services.ingest import IngestError, PageIngestService


async def _main() -> None:
    settings = load_settings()
    if not settings.openai_api_key:
        raise SystemExit("Set OPENAI_API_KEY before re-indexing pages.")
    logging.basicConfig(level=logging.INFO)
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    embeddings = EmbeddingClient(client, settings.openai_embedding_model)
    chunk_store = ChromaChunkStore(settings.chroma_path)
    ingest = PageIngestService(settings, chunk_store, embeddings)
    try:
        indexed = await ingest.reset_pages()
    except IngestError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Indexed {len(indexed)} pages: {', '.join(indexed)}")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
