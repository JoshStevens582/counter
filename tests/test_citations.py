from counter.schemas.chat import RetrievedChunk
from counter.services.citations import mark_cited_chunks, parse_citation_numbers


def _chunk(n: int) -> RetrievedChunk:
    return RetrievedChunk(
        document_id="fees",
        document_title="Session fees",
        chunk_index=0,
        text="R650",
        distance=0.1,
        cite_n=n,
    )


def test_parse_citation_numbers_drops_fake() -> None:
    assert parse_citation_numbers("It costs R650 [1] and more [99].", 2) == [1]


def test_mark_cited_chunks() -> None:
    chunks = [_chunk(1), _chunk(2)]
    marked = mark_cited_chunks(chunks, "Session fee is R650 [1].")
    assert marked[0].cited is True
    assert marked[1].cited is False
