"""Conditional routing for iteration, HITL and fan-out research."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.types import Send

from atlas.graph.state import ResearchState
from atlas.models.enums import HumanDecision


def dispatch_research(state: ResearchState) -> list[Send] | Literal["analyse"]:
    plan = state.get("research_plan") or []
    if not plan:
        return "analyse"
    sends: list[Send] = []
    for task in plan:
        payload: dict[str, Any] = {
            "research_id": state["research_id"],
            "user_query": state["user_query"],
            "current_task": task,
            "iteration": state.get("iteration", 0),
            "sources_reviewed": state.get("sources_reviewed", 0),
        }
        sends.append(Send("research_task", payload))
    return sends


def after_analyse(state: ResearchState) -> Literal["plan", "synthesise"]:
    if state.get("needs_more_research"):
        return "plan"
    return "synthesise"


def after_verify(state: ResearchState) -> Literal["plan", "critic"]:
    if state.get("needs_more_research"):
        return "plan"
    return "critic"


def after_human(state: ResearchState) -> Literal["plan", "finalise", "cancelled", "awaiting"]:
    if state.get("status") == "awaiting_human" and not state.get("human_decision"):
        return "awaiting"
    decision = (state.get("human_decision") or HumanDecision.APPROVE.value).lower()
    if decision == HumanDecision.CANCEL.value:
        return "cancelled"
    if decision == HumanDecision.REQUEST_MORE_RESEARCH.value:
        if int(state.get("iteration") or 0) >= 2:
            return "finalise"
        return "plan"
    return "finalise"
