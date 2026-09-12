"""Explicit memory rules: conversation history is never auto-promoted."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.models.memory import MemoryItem
from atlas.repositories.memory_repository import MemoryRepository

ALLOWED_CATEGORIES = {
    "preference",
    "company_background",
    "research_criteria",
    "report_format",
}


class MemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MemoryRepository(session)

    async def remember(self, item: MemoryItem) -> MemoryItem:
        if item.category not in ALLOWED_CATEGORIES:
            raise ValueError(f"unsupported memory category: {item.category}")
        return await self.repo.upsert(item)

    async def list_items(self) -> list[MemoryItem]:
        return await self.repo.list_all()

    async def forget(self, memory_id: str) -> bool:
        return await self.repo.delete(memory_id)
