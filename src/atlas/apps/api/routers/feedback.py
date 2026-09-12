"""Human feedback and inspectable memory."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.apps.api.deps import session_dep
from atlas.apps.api.errors import ApiError
from atlas.apps.api.schemas import FeedbackRequest, MemoryCreateRequest
from atlas.memory.store import MemoryService
from atlas.models.feedback import Feedback
from atlas.models.memory import MemoryItem
from atlas.repositories.research_repository import ResearchRepository

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
async def create_feedback(
    body: FeedbackRequest,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, str]:
    feedback = Feedback(
        research_id=body.research_id,
        rating=body.rating,
        comments=body.comments,
        useful_sections=body.useful_sections,
        flagged_errors=body.flagged_errors,
    )
    await ResearchRepository(session).add_feedback(feedback)
    await session.commit()
    return {"id": feedback.id}


@router.get("/memory")
async def list_memory(session: AsyncSession = Depends(session_dep)) -> dict[str, object]:
    items = await MemoryService(session).list_items()
    return {"items": [item.model_dump(mode="json") for item in items]}


@router.post("/memory")
async def create_memory(
    body: MemoryCreateRequest,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, object]:
    item = await MemoryService(session).remember(
        MemoryItem(key=body.key, value=body.value, category=body.category, pinned=body.pinned)
    )
    await session.commit()
    return item.model_dump(mode="json")


@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, bool]:
    deleted = await MemoryService(session).forget(memory_id)
    if not deleted:
        raise ApiError("memory not found or pinned", status_code=404, code="not_found")
    await session.commit()
    return {"deleted": True}
