"""FastAPI dependencies."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.config.settings import Settings
from atlas.persistence.session import get_session
from atlas.rag.retrieval import HybridRetriever
from atlas.services.orchestrator import ResearchOrchestrator
from atlas.services.runtime import Runtime


def settings_dep(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def runtime_dep(request: Request) -> Runtime:
    return request.app.state.runtime  # type: ignore[no-any-return]


async def session_dep() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


async def orchestrator_dep(
    session: AsyncSession = Depends(session_dep),
    settings: Settings = Depends(settings_dep),
    runtime: Runtime = Depends(runtime_dep),
) -> ResearchOrchestrator:
    if runtime.retriever is None:
        runtime.bind_retriever(
            HybridRetriever(
                repository=__import__(
                    "atlas.repositories.document_repository", fromlist=["DocumentRepository"]
                ).DocumentRepository(session),
                embeddings=runtime.embeddings,
                settings=settings,
            )
        )
    return ResearchOrchestrator(session, settings, runtime)
