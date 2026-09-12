"""Strongly typed LangGraph state. Structured artefacts, not a chat dump."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


def last_value(existing: Any, new: Any) -> Any:
    """Reducer for scalar fields written by parallel research nodes."""
    return new if new is not None else existing


class ResearchState(TypedDict, total=False):
    research_id: str
    user_query: str
    intent: str
    high_impact: bool
    sensitive: bool
    research_plan: list[dict[str, Any]]
    current_task: dict[str, Any] | None
    completed_tasks: Annotated[list[dict[str, Any]], operator.add]
    evidence: Annotated[list[dict[str, Any]], operator.add]
    contradictions: list[dict[str, Any]]
    unanswered_questions: list[str]
    confidence: dict[str, Any] | None
    confidence_score: float
    draft_report: str | None
    final_report: str | None
    report: dict[str, Any] | None
    critic: dict[str, Any] | None
    verification: dict[str, Any] | None
    iteration: int
    status: Annotated[str, last_value]
    needs_more_research: bool
    human_decision: str | None
    interrupt_payload: dict[str, Any] | None
    errors: Annotated[list[str], operator.add]
    progress: Annotated[list[str], operator.add]
    budget: dict[str, Any]
    sources_reviewed: Annotated[int, operator.add]
