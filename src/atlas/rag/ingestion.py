"""Document ingestion: parse → metadata → chunk → embed → pgvector."""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.config.settings import Settings
from atlas.llm.embeddings import EmbeddingClient
from atlas.observability.logging import get_logger
from atlas.persistence.orm import DocumentChunkRow
from atlas.rag.chunking import chunk_document
from atlas.rag.parsers import parse_bytes
from atlas.repositories.document_repository import DocumentRepository
from atlas.security.uploads import validate_upload

logger = get_logger(__name__)


class IngestionService:
    def __init__(
        self,
        session: AsyncSession,
        embeddings: EmbeddingClient,
        settings: Settings,
    ) -> None:
        self.session = session
        self.embeddings = embeddings
        self.settings = settings
        self.documents = DocumentRepository(session)

    async def ingest_path(self, path: Path, *, source: str = "upload") -> str:
        data = await asyncio.to_thread(path.read_bytes)
        filename = validate_upload(
            path.name, None, len(data), self.settings
        )
        return await self.ingest_bytes(filename, data, source=source)

    async def ingest_bytes(
        self,
        filename: str,
        data: bytes,
        *,
        source: str = "upload",
        content_type: str | None = None,
    ) -> str:
        safe_name = validate_upload(filename, content_type, len(data), self.settings)
        checksum = hashlib.sha256(data).hexdigest()
        parsed = parse_bytes(safe_name, data)
        document = await self.documents.create_document(
            filename=safe_name,
            source=source,
            content_type=parsed.content_type,
            checksum=checksum,
            byte_size=len(data),
            metadata={"original_filename": filename},
        )
        chunks = chunk_document(
            parsed,
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
        )
        embeddings = await self.embeddings.embed([chunk.content for chunk in chunks]) if chunks else []
        rows = [
            DocumentChunkRow(
                document_id=document.id,
                filename=safe_name,
                source=source,
                page=chunk.page,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                embedding=vector,
            )
            for chunk, vector in zip(chunks, embeddings, strict=True)
        ]
        if rows:
            await self.documents.add_chunks(rows)
        await self.session.commit()
        logger.info(
            "document_ingested",
            document_id=document.id,
            filename=safe_name,
            chunks=len(rows),
        )
        return document.id
