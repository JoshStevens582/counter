class ChunkingError(ValueError):
    """Raised when chunk size and overlap cannot produce progress."""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size < 1:
        raise ChunkingError("chunk_size must be at least 1.")
    if overlap < 0:
        raise ChunkingError("overlap cannot be negative.")
    if overlap >= chunk_size:
        raise ChunkingError("chunk_size must be bigger than overlap.")

    stripped = text.strip()
    if not stripped:
        return []

    chunks: list[str] = []
    start = 0
    length = len(stripped)

    while True:
        end = start + chunk_size
        if end > length:
            end = length
        piece = stripped[start:end]
        if piece:
            chunks.append(piece)
        if end == length:
            break
        start = end - overlap

    return chunks


def chunk_document(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not text.strip():
        return []

    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = paragraph if not buffer else f"{buffer}\n\n{paragraph}"
        if len(candidate) <= chunk_size:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
            buffer = ""
        if len(paragraph) <= chunk_size:
            buffer = paragraph
        else:
            chunks.extend(chunk_text(paragraph, chunk_size, overlap))
    if buffer:
        chunks.append(buffer)
    return chunks
