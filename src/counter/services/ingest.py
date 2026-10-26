import asyncio
import logging
from pathlib import Path

from counter.config import Settings
from counter.repositories.chroma_repo import ChromaChunkStore
from counter.services.chunking import chunk_document
from counter.services.embeddings import EmbeddingClient
from counter.services.readers import (
    SUPPORTED_SUFFIXES,
    read_page_text,
    title_from_path,
    title_from_text,
)

logger = logging.getLogger("counter.ingest")


class IngestError(ValueError):
    """Raised when a page cannot be indexed."""


class PageIngestService:
    def __init__(
        self,
        settings: Settings,
        chunk_store: ChromaChunkStore,
        embeddings: EmbeddingClient,
    ) -> None:
        self._settings = settings
        self._chunk_store = chunk_store
        self._embeddings = embeddings

    def page_file_count(self) -> int:
        return len(self._page_paths())

    def _page_paths(self) -> list[Path]:
        pages_dir = Path(self._settings.pages_dir)
        if not pages_dir.is_dir():
            return []
        return sorted(
            path
            for path in pages_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        )

    async def ingest_path(self, path: Path) -> str:
        text = read_page_text(path)
        title = title_from_text(text, title_from_path(path))
        document_id = path.stem
        chunks = chunk_document(
            text,
            self._settings.chunk_size,
            self._settings.chunk_overlap,
        )
        if not chunks:
            raise IngestError(f"{path.name} produced no text chunks.")

        vectors = await self._embeddings.embed_texts(chunks)
        if len(vectors) != len(chunks):
            raise IngestError("Embedding count did not match chunk count.")

        await asyncio.to_thread(
            self._chunk_store.upsert_chunks,
            document_id,
            title,
            chunks,
            vectors,
        )
        logger.info("Indexed page %s (%s chunks)", document_id, len(chunks))
        return document_id

    async def seed_pages(self) -> list[str]:
        """Index demo pages once when Chroma is empty."""
        if self._chunk_store.count() > 0:
            return []
        paths = self._page_paths()
        if not paths:
            raise IngestError(f"No pages found in {self._settings.pages_dir}.")
        indexed: list[str] = []
        for path in paths:
            indexed.append(await self.ingest_path(path))
        return indexed

    async def reset_pages(self) -> list[str]:
        paths = self._page_paths()
        if not paths:
            raise IngestError(f"No pages found in {self._settings.pages_dir}.")
        await asyncio.to_thread(self._chunk_store.reset)
        indexed: list[str] = []
        for path in paths:
            indexed.append(await self.ingest_path(path))
        return indexed
