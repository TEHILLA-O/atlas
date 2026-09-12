"""Token-aware chunking with overlap and metadata preservation."""

from __future__ import annotations

from dataclasses import dataclass

from atlas.rag.parsers import ParsedDocument


@dataclass(slots=True)
class Chunk:
    content: str
    chunk_index: int
    page: int | None
    section: str | None
    filename: str


def chunk_document(
    document: ParsedDocument,
    *,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[Chunk]:
    if chunk_size < 50:
        raise ValueError("chunk_size must be >= 50")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    index = 0
    for page in document.pages:
        tokens = _split_words(page.text)
        if not tokens:
            continue
        start = 0
        while start < len(tokens):
            end = min(len(tokens), start + chunk_size)
            window = tokens[start:end]
            content = " ".join(window).strip()
            if content:
                chunks.append(
                    Chunk(
                        content=content,
                        chunk_index=index,
                        page=page.page,
                        section=page.section,
                        filename=document.filename,
                    )
                )
                index += 1
            if end == len(tokens):
                break
            start = end - overlap
    return chunks


def _split_words(text: str) -> list[str]:
    return [part for part in text.replace("\n", " ").split(" ") if part]
