from __future__ import annotations

import pytest

from atlas.config.settings import Settings
from atlas.graph.context import GraphContext
from atlas.graph.workflow import compile_research_graph, memory_checkpointer
from atlas.llm.providers.demo import DemoLLM
from atlas.services.runtime import build_tool_registry


@pytest.mark.asyncio
@pytest.mark.graph
async def test_full_graph_completes_in_demo_mode() -> None:
    settings = Settings(env="test", model_provider="demo", hitl_enabled=False, max_iterations=2)
    llm = DemoLLM()
    tools = build_tool_registry(settings)
    context = GraphContext.build(settings, llm, tools)
    graph = compile_research_graph(memory_checkpointer())
    result = await graph.ainvoke(
        {
            "research_id": "demo-1",
            "user_query": (
                "Analyse whether Acme Technology should enter the UK public-sector "
                "cybersecurity market."
            ),
            "completed_tasks": [],
            "evidence": [],
            "errors": [],
            "progress": [],
            "iteration": 0,
            "sources_reviewed": 0,
        },
        config={"configurable": {"thread_id": "demo-1", "atlas": context}},
    )
    assert result["status"] == "completed"
    assert result["research_plan"]
    assert result["evidence"]
    assert result["final_report"]
    assert "Executive Summary" in result["final_report"]
    assert result["confidence_score"] is not None
    assert result.get("iteration", 0) <= settings.max_iterations


@pytest.mark.asyncio
@pytest.mark.graph
async def test_human_cancel_stops_report() -> None:
    settings = Settings(env="test", model_provider="demo", hitl_enabled=False)
    context = GraphContext.build(settings, DemoLLM(), build_tool_registry(settings))
    graph = compile_research_graph(memory_checkpointer())
    result = await graph.ainvoke(
        {
            "research_id": "cancel-1",
            "user_query": "Research a technology market and identify risks.",
            "completed_tasks": [],
            "evidence": [],
            "errors": [],
            "progress": [],
            "iteration": 0,
            "sources_reviewed": 0,
            "human_decision": "cancel",
        },
        config={"configurable": {"thread_id": "cancel-1", "atlas": context}},
    )
    assert result["status"] == "cancelled"
    assert result.get("final_report") is None


@pytest.mark.asyncio
@pytest.mark.graph
async def test_max_iteration_guard_stops_replan() -> None:
    from atlas.graph.routing import after_analyse

    assert after_analyse({"needs_more_research": False, "iteration": 9}) == "synthesise"
