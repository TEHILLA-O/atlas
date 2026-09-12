"""Typed tool protocol used by every Atlas tool."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class ToolError(BaseModel):
    tool: str
    message: str
    retryable: bool = False


class ToolResult(BaseModel):
    tool: str
    ok: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    error: ToolError | None = None


class AtlasTool(Protocol):
    name: str
    description: str
    input_model: Any

    async def run(self, payload: BaseModel) -> ToolResult: ...
