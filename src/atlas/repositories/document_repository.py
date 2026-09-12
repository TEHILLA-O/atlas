"""Document and chunk persistence including hybrid retrieval helpers."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.persistence.orm import DocumentChunkRow, DocumentRow


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_document(
        self,
        *,
        filename: str,
        source: str,
        content_type: str,
        checksum: str,
        byte_size: int,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentRow:
        row = DocumentRow(
            filename=filename,
            source=source,
            content_type=content_type,
            checksum=checksum,
            byte_size=byte_size,
            extra=metadata or {},
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def get(self, document_id: str) -> DocumentRow | None:
        return await self.session.get(DocumentRow, document_id)

    async def list_documents(self, *, limit: int = 50, offset: int = 0) -> list[DocumentRow]:
        result = await self.session.scalars(
            select(DocumentRow).order_by(DocumentRow.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result)

    async def delete(self, document_id: str) -> bool:
        row = await self.get(document_id)
        if row is None:
            return False
        await self.session.delete(row)
        return True

    async def add_chunks(self, chunks: list[DocumentChunkRow]) -> None:
        self.session.add_all(chunks)
        await self.session.flush()

    async def vector_search(
        self,
        embedding: list[float],
        *,
        top_k: int,
        document_ids: list[str] | None = None,
        min_similarity: float = 0.0,
    ) -> list[tuple[DocumentChunkRow, float]]:
        distance = DocumentChunkRow.embedding.cosine_distance(embedding)
        similarity = (1 - distance).label("similarity")
        stmt: Select[Any] = (
            select(DocumentChunkRow, similarity)
            .where(DocumentChunkRow.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )
        if document_ids:
            stmt = stmt.where(DocumentChunkRow.document_id.in_(document_ids))
        rows = await self.session.execute(stmt)
        results: list[tuple[DocumentChunkRow, float]] = []
        for chunk, score in rows.all():
            if float(score) >= min_similarity:
                results.append((chunk, float(score)))
        return results

    async def keyword_search(
        self,
        query: str,
        *,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[tuple[DocumentChunkRow, float]]:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank_cd(
            func.to_tsvector("english", DocumentChunkRow.content), ts_query
        ).label("rank")
        stmt: Select[Any] = (
            select(DocumentChunkRow, rank)
            .where(func.to_tsvector("english", DocumentChunkRow.content).op("@@")(ts_query))
            .order_by(rank.desc())
            .limit(top_k)
        )
        if document_ids:
            stmt = stmt.where(DocumentChunkRow.document_id.in_(document_ids))
        rows = await self.session.execute(stmt)
        return [(chunk, float(score or 0.0)) for chunk, score in rows.all()]

    async def ensure_pgvector(self) -> None:
        await self.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
