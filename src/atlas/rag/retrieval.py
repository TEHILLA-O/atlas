"""Hybrid retrieval: rewrite → vector + keyword → RRF → rerank → dedup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.config.settings import Settings
from atlas.llm.embeddings import EmbeddingClient
from atlas.rag.query_rewrite import rewrite_query
from atlas.rag.reranking import RankedItem, lexical_rerank, merge_rrf
from atlas.repositories.document_repository import DocumentRepository


@dataclass(slots=True)
class RetrievedChunk:
    document_id: str
    filename: str
    content: str
    page: int | None
    section: str | None
    chunk_index: int
    score: float
    metadata: dict[str, Any]


class HybridRetriever:
    def __init__(
        self,
        repository: DocumentRepository,
        embeddings: EmbeddingClient,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.embeddings = embeddings
        self.settings = settings

    async def retrieve(
        self,
        query: str,
        *,
        document_ids: list[str] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        variants = rewrite_query(query)
        primary = variants[0]
        vectors = await self.embeddings.embed([primary])
        top = top_k or self.settings.top_k
        vector_rows = await self.repository.vector_search(
            vectors[0],
            top_k=top,
            document_ids=document_ids,
            min_similarity=self.settings.min_similarity,
        )
        keyword_rows: list[tuple[Any, float]] = []
        for variant in variants:
            keyword_rows.extend(
                await self.repository.keyword_search(
                    variant, top_k=top, document_ids=document_ids
                )
            )
        vector_items = [
            RankedItem(text=chunk.content, score=score, payload=chunk)
            for chunk, score in vector_rows
        ]
        keyword_items = [
            RankedItem(text=chunk.content, score=score, payload=chunk)
            for chunk, score in keyword_rows
        ]
        fused = merge_rrf(vector_items, keyword_items)
        reranked = lexical_rerank(primary, fused, rerank_k=self.settings.rerank_k)
        return [_to_chunk(item) for item in _deduplicate(reranked)]


def _to_chunk(item: RankedItem) -> RetrievedChunk:
    chunk = item.payload
    return RetrievedChunk(
        document_id=chunk.document_id,
        filename=chunk.filename,
        content=chunk.content,
        page=chunk.page,
        section=chunk.section,
        chunk_index=chunk.chunk_index,
        score=min(1.0, max(0.0, item.score if item.score <= 1 else item.score / 10)),
        metadata={"source": chunk.source},
    )


def _deduplicate(items: list[RankedItem]) -> list[RankedItem]:
    seen: set[str] = set()
    unique: list[RankedItem] = []
    for item in items:
        key = item.text[:200]
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
