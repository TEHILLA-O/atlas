"""Least-privilege tool registry. Agents request tools by name only."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ValidationError

from atlas.tools.base import AtlasTool, ToolError, ToolResult


class ToolRegistry:
    def __init__(self, tools: Iterable[AtlasTool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def available(self) -> list[str]:
        return sorted(self._tools)

    def descriptions(self, names: Iterable[str]) -> dict[str, str]:
        return {name: self._tools[name].description for name in names if name in self._tools}

    def restrict(self, names: Iterable[str]) -> ToolRegistry:
        allowed = {name: self._tools[name] for name in names if name in self._tools}
        subset = ToolRegistry([])
        subset._tools = allowed
        return subset

    async def invoke(self, name: str, raw: dict[str, object]) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                tool=name,
                ok=False,
                error=ToolError(tool=name, message="tool not permitted", retryable=False),
            )
        try:
            payload: BaseModel = tool.input_model.model_validate(raw)
        except ValidationError as exc:
            return ToolResult(
                tool=name,
                ok=False,
                error=ToolError(tool=name, message=str(exc), retryable=False),
            )
        return await tool.run(payload)


def build_default_registry(
    *,
    web_search: AtlasTool,
    web_fetch: AtlasTool,
    document_search: AtlasTool,
    retrieve_chunks: AtlasTool,
    calculator: AtlasTool,
    database_search: AtlasTool,
    previous_research: AtlasTool,
) -> ToolRegistry:
    return ToolRegistry(
        [
            web_search,
            web_fetch,
            document_search,
            retrieve_chunks,
            calculator,
            database_search,
            previous_research,
        ]
    )
