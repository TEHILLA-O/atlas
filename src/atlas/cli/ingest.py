"""Ingest demo or local documents into pgvector."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from atlas.config.settings import get_settings
from atlas.llm.embeddings import build_embedding_client
from atlas.persistence.session import async_session_factory
from atlas.rag.ingestion import IngestionService


async def _ingest(paths: list[Path]) -> None:
    settings = get_settings()
    embeddings = build_embedding_client(settings)
    factory = async_session_factory(settings)
    async with factory() as session:
        service = IngestionService(session, embeddings, settings)
        for path in paths:
            document_id = await service.ingest_path(path)
            print(f"ingested {path.name} -> {document_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into Atlas")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    asyncio.run(_ingest(args.paths))
