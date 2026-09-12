"""Private-document search and chunk retrieval tools."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field

from atlas.rag.retrieval import RetrievedChunk
from atlas.tools.base import ToolError, ToolResult


class DocumentSearchInput(BaseModel):
    query: str = Field(description="Natural-language query over uploaded documents.")
    document_ids: list[str] = Field(default_factory=list)


class RetrieveChunksInput(BaseModel):
    query: str
    top_k: int = Field(default=8, ge=1, le=20)
    document_ids: list[str] = Field(default_factory=list)


RetrieveFn = Callable[..., Awaitable[list[RetrievedChunk]]]


class DocumentSearchTool:
    name = "search_documents"
    description = "Search uploaded private documents using hybrid retrieval."
    input_model = DocumentSearchInput

    def __init__(self, retrieve: RetrieveFn) -> None:
        self._retrieve = retrieve

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, DocumentSearchInput)
        try:
            chunks = await self._retrieve(
                payload.query,
                document_ids=payload.document_ids or None,
            )
        except Exception as exc:
            return ToolResult(
                tool=self.name,
                ok=False,
                error=ToolError(tool=self.name, message=str(exc), retryable=True),
            )
        return ToolResult(
            tool=self.name,
            data={"results": [_chunk_dict(chunk) for chunk in chunks]},
        )


class RetrieveChunksTool:
    name = "retrieve_document_chunks"
    description = "Retrieve the most relevant private document chunks for a focused question."
    input_model = RetrieveChunksInput

    def __init__(self, retrieve: RetrieveFn) -> None:
        self._retrieve = retrieve

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, RetrieveChunksInput)
        chunks = await self._retrieve(
            payload.query,
            document_ids=payload.document_ids or None,
            top_k=payload.top_k,
        )
        return ToolResult(
            tool=self.name,
            data={"results": [_chunk_dict(chunk) for chunk in chunks]},
        )


def _chunk_dict(chunk: RetrievedChunk) -> dict[str, object]:
    return {
        "document_id": chunk.document_id,
        "filename": chunk.filename,
        "content": chunk.content,
        "page": chunk.page,
        "section": chunk.section,
        "score": chunk.score,
    }
