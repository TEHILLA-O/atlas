"""Research planner: question → structured subtasks with source constraints."""

from __future__ import annotations

from atlas.agents.schemas import ClassificationResult, QueryBundle, ResearchPlan
from atlas.config.settings import Settings
from atlas.llm.factory import LLMClient
from atlas.models.research import ResearchTask
from atlas.prompts.templates import CLASSIFIER_SYSTEM, PLANNER_SYSTEM


class PlannerAgent:
    """Owns classification, planning and query generation. No retrieval tools."""

    def __init__(self, llm: LLMClient, settings: Settings) -> None:
        self.llm = llm
        self.settings = settings

    async def classify(self, query: str) -> ClassificationResult:
        result = await self.llm.structured(
            f"Classify this research request:\n{query}",
            ClassificationResult,
            system=CLASSIFIER_SYSTEM,
        )
        assert isinstance(result, ClassificationResult)
        return result

    async def plan(self, query: str, intent: str) -> list[ResearchTask]:
        result = await self.llm.structured(
            f"Intent: {intent}\nUser request:\n{query}\n"
            f"Create at most {self.settings.max_research_tasks} tasks.",
            ResearchPlan,
            system=PLANNER_SYSTEM,
        )
        assert isinstance(result, ResearchPlan)
        tasks = result.tasks[: self.settings.max_research_tasks]
        for index, task in enumerate(tasks, start=1):
            task.priority = task.priority or index
        return tasks

    async def queries_for(self, task: ResearchTask) -> list[str]:
        result = await self.llm.structured(
            f"Generate 2-4 search queries for: {task.question}\nPurpose: {task.purpose}",
            QueryBundle,
            system=PLANNER_SYSTEM,
        )
        assert isinstance(result, QueryBundle)
        return result.queries or [task.question]
