from __future__ import annotations

import pytest

from atlas.agents.planner import PlannerAgent
from atlas.config.settings import Settings
from atlas.llm.providers.demo import DemoLLM


@pytest.mark.asyncio
async def test_planner_returns_structured_tasks() -> None:
    agent = PlannerAgent(DemoLLM(), Settings(max_research_tasks=8))
    classified = await agent.classify(
        "Analyse whether Acme Technology should enter the UK public-sector cybersecurity market."
    )
    tasks = await agent.plan(
        "Analyse whether Acme Technology should enter the UK public-sector cybersecurity market.",
        classified.intent.value,
    )
    assert classified.intent.value == "opportunity_assessment"
    assert 1 <= len(tasks) <= 8
    assert all(task.question and task.purpose for task in tasks)
    assert all(task.source_types for task in tasks)
