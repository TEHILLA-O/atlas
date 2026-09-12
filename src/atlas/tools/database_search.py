"""Read-only lookup over persisted research artefacts."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field

from atlas.tools.base import ToolResult


class DatabaseSearchInput(BaseModel):
    research_id: str | None = None
    topic: str = Field(description="Topic or keyword to look up in prior research.")


class PreviousResearchInput(BaseModel):
    query: str


class DatabaseSearchTool:
    name = "query_database"
    description = "Look up structured evidence or prior session metadata from PostgreSQL."
    input_model = DatabaseSearchInput

    def __init__(self, lookup: Callable[[str], Awaitable[list[dict[str, object]]]]) -> None:
        self._lookup = lookup

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, DatabaseSearchInput)
        rows = await self._lookup(payload.topic)
        return ToolResult(tool=self.name, data={"results": rows})


class PreviousResearchTool:
    name = "search_previous_research"
    description = "Search summaries from earlier Atlas research sessions."
    input_model = PreviousResearchInput

    def __init__(self, lookup: Callable[[str], Awaitable[list[dict[str, object]]]]) -> None:
        self._lookup = lookup

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, PreviousResearchInput)
        rows = await self._lookup(payload.query)
        return ToolResult(tool=self.name, data={"results": rows})
