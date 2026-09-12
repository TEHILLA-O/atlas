"""Compile the Atlas research state machine."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from atlas.graph.nodes import (
    analyse_node,
    classify_node,
    critic_node,
    finalise_node,
    human_review_node,
    plan_node,
    research_task_node,
    synthesise_node,
    verify_node,
)
from atlas.graph.routing import after_analyse, after_human, after_verify, dispatch_research
from atlas.graph.state import ResearchState


def build_research_graph() -> StateGraph[ResearchState]:
    graph: StateGraph[ResearchState] = StateGraph(ResearchState)
    graph.add_node("classify", classify_node)
    graph.add_node("plan", plan_node)
    graph.add_node("research_task", research_task_node)
    graph.add_node("analyse", analyse_node)
    graph.add_node("synthesise", synthesise_node)
    graph.add_node("verify", verify_node)
    graph.add_node("critic", critic_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("finalise", finalise_node)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "plan")
    graph.add_conditional_edges("plan", dispatch_research, ["research_task", "analyse"])
    graph.add_edge("research_task", "analyse")
    graph.add_conditional_edges("analyse", after_analyse, {"plan": "plan", "synthesise": "synthesise"})
    graph.add_edge("synthesise", "verify")
    graph.add_conditional_edges("verify", after_verify, {"plan": "plan", "critic": "critic"})
    graph.add_edge("critic", "human_review")
    graph.add_conditional_edges(
        "human_review",
        after_human,
        {"plan": "plan", "finalise": "finalise", "cancelled": "finalise", "awaiting": END},
    )
    graph.add_edge("finalise", END)
    return graph


def compile_research_graph(
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> Any:
    """Compile with a checkpointer so sessions survive restarts and can resume."""
    saver = checkpointer or MemorySaver()
    return build_research_graph().compile(checkpointer=saver)


def memory_checkpointer() -> MemorySaver:
    return MemorySaver()
