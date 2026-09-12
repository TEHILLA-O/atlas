"""Research session endpoints including SSE progress."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from atlas.apps.api.deps import orchestrator_dep, session_dep
from atlas.apps.api.errors import ApiError
from atlas.apps.api.schemas import ResearchCreateRequest, ResumeRequest
from atlas.observability.events import progress_bus
from atlas.repositories.research_repository import ResearchRepository
from atlas.services.orchestrator import ResearchOrchestrator

router = APIRouter(prefix="/research", tags=["research"])


@router.post("")
async def create_research(
    body: ResearchCreateRequest,
    orchestrator: ResearchOrchestrator = Depends(orchestrator_dep),
) -> dict[str, object]:
    return await orchestrator.start(body.query)


@router.get("/{research_id}")
async def get_research(
    research_id: str,
    orchestrator: ResearchOrchestrator = Depends(orchestrator_dep),
) -> dict[str, object]:
    snap = await orchestrator.snapshot(research_id)
    if snap is None:
        raise ApiError("research not found", status_code=404, code="not_found")
    return snap


@router.post("/{research_id}/resume")
async def resume_research(
    research_id: str,
    body: ResumeRequest,
    orchestrator: ResearchOrchestrator = Depends(orchestrator_dep),
) -> dict[str, object]:
    return await orchestrator.resume(research_id, body.decision)


@router.post("/{research_id}/cancel")
async def cancel_research(
    research_id: str,
    orchestrator: ResearchOrchestrator = Depends(orchestrator_dep),
) -> dict[str, str]:
    await orchestrator.cancel(research_id)
    return {"status": "cancelled"}


@router.get("/{research_id}/evidence")
async def list_evidence(
    research_id: str,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, object]:
    items = await ResearchRepository(session).list_evidence(research_id)
    return {"items": [item.model_dump(mode="json") for item in items]}


@router.get("/{research_id}/contradictions")
async def list_contradictions(
    research_id: str,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, object]:
    items = await ResearchRepository(session).list_contradictions(research_id)
    return {"items": [item.model_dump(mode="json") for item in items]}


@router.get("/{research_id}/report")
async def get_report(
    research_id: str,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, object]:
    row = await ResearchRepository(session).latest_report(research_id)
    if row is None:
        raise ApiError("report not found", status_code=404, code="not_found")
    return {"title": row.title, "markdown": row.markdown, "payload": row.payload}


@router.get("/{research_id}/events")
async def stream_events(research_id: str) -> EventSourceResponse:
    async def generator() -> Any:
        for event in progress_bus.history(research_id):
            yield {"event": "progress", "data": json.dumps(event)}
        async for payload in progress_bus.subscribe(research_id):
            yield {"event": "progress", "data": payload}

    return EventSourceResponse(generator())
