from __future__ import annotations

import pytest

from atlas.config.settings import Settings
from atlas.services.runtime import build_tool_registry


@pytest.mark.asyncio
async def test_least_privilege_and_typed_errors() -> None:
    registry = build_tool_registry(Settings())
    web = registry.restrict(["web_search"])
    denied = await web.invoke("calculator", {"expression": "1+1"})
    assert denied.ok is False
    assert denied.error is not None
    result = await registry.invoke("web_search", {"query": "Cyber Essentials Plus public sector"})
    assert result.ok
    assert result.data["results"]
