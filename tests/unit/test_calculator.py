from __future__ import annotations

import pytest

from atlas.tools.calculator import CalculatorInput, CalculatorTool


@pytest.mark.asyncio
async def test_calculator_evaluates_safe_expression() -> None:
    result = await CalculatorTool().run(CalculatorInput(expression="(10 + 5) * 2"))
    assert result.ok
    assert result.data["value"] == 30.0


@pytest.mark.asyncio
async def test_calculator_rejects_attribute_access() -> None:
    result = await CalculatorTool().run(CalculatorInput(expression="__import__('os').system('echo')"))
    assert result.ok is False
    assert result.error is not None
