"""Safe arithmetic tool for numeric consistency checks."""

from __future__ import annotations

import ast
import operator
from typing import Any

from pydantic import BaseModel, Field

from atlas.tools.base import ToolError, ToolResult

_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


class CalculatorInput(BaseModel):
    expression: str = Field(description="Arithmetic expression using + - * / ** and parentheses.")


class CalculatorTool:
    name = "calculator"
    description = "Evaluate a simple arithmetic expression. Use for totals, percentages and numeric checks."
    input_model = CalculatorInput

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, CalculatorInput)
        try:
            value = _eval(payload.expression)
        except Exception as exc:
            return ToolResult(
                tool=self.name,
                ok=False,
                error=ToolError(tool=self.name, message=str(exc), retryable=False),
            )
        return ToolResult(tool=self.name, data={"expression": payload.expression, "value": value})


def _eval(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return float(_eval_node(tree.body))


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return float(_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return float(_OPS[type(node.op)](_eval_node(node.operand)))
    raise ValueError("unsupported expression")
