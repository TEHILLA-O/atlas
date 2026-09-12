from __future__ import annotations

import pytest

from atlas.rag.chunking import chunk_document
from atlas.rag.parsers import ParsedDocument, ParsedPage


def test_chunking_respects_overlap_and_index() -> None:
    words = " ".join(f"w{i}" for i in range(250))
    document = ParsedDocument(
        filename="note.txt",
        content_type="text/plain",
        pages=[ParsedPage(text=words, page=1, section="body")],
    )
    chunks = chunk_document(document, chunk_size=100, overlap=20)
    assert len(chunks) >= 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].filename == "note.txt"


def test_chunking_rejects_invalid_overlap() -> None:
    document = ParsedDocument(
        filename="x.txt",
        content_type="text/plain",
        pages=[ParsedPage(text="hello world", page=1)],
    )
    with pytest.raises(ValueError):
        chunk_document(document, chunk_size=80, overlap=80)
