"""Inspectable, removable long-term memory. Not conversation history."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.models.memory import MemoryItem
from atlas.persistence.orm import MemoryRow


class MemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, item: MemoryItem) -> MemoryItem:
        existing = await self.session.scalar(
            select(MemoryRow).where(MemoryRow.key == item.key)
        )
        if existing:
            existing.value = item.value
            existing.category = item.category
            existing.pinned = item.pinned
            existing.extra = item.metadata
            return item
        self.session.add(
            MemoryRow(
                id=item.id,
                key=item.key,
                value=item.value,
                category=item.category,
                pinned=item.pinned,
                extra=item.metadata,
            )
        )
        return item

    async def list_all(self) -> list[MemoryItem]:
        rows = await self.session.scalars(select(MemoryRow).order_by(MemoryRow.created_at.desc()))
        return [
            MemoryItem(
                id=row.id,
                key=row.key,
                value=row.value,
                category=row.category,
                pinned=row.pinned,
                metadata=row.extra or {},
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def delete(self, memory_id: str) -> bool:
        row = await self.session.get(MemoryRow, memory_id)
        if row is None or row.pinned:
            return False
        await self.session.delete(row)
        return True
