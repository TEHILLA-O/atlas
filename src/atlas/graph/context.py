"""Runtime dependencies injected through LangGraph configurable state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.agents.critic import CriticAgent
from atlas.agents.document_analyst import DocumentAnalystAgent
from atlas.agents.planner import PlannerAgent
from atlas.agents.researcher import ResearcherAgent
from atlas.agents.synthesizer import SynthesizerAgent
from atlas.agents.verifier import VerifierAgent
from atlas.config.settings import Settings
from atlas.llm.factory import LLMClient
from atlas.services.budget import BudgetTracker
from atlas.tools.registry import ToolRegistry


@dataclass
class GraphContext:
    settings: Settings
    llm: LLMClient
    tools: ToolRegistry
    planner: PlannerAgent
    researcher: ResearcherAgent
    document_analyst: DocumentAnalystAgent
    verifier: VerifierAgent
    critic: CriticAgent
    synthesizer: SynthesizerAgent
    budget: BudgetTracker

    @classmethod
    def build(cls, settings: Settings, llm: LLMClient, tools: ToolRegistry) -> GraphContext:
        return cls(
            settings=settings,
            llm=llm,
            tools=tools,
            planner=PlannerAgent(llm, settings),
            researcher=ResearcherAgent(llm, tools),
            document_analyst=DocumentAnalystAgent(llm, tools),
            verifier=VerifierAgent(llm),
            critic=CriticAgent(llm),
            synthesizer=SynthesizerAgent(llm),
            budget=BudgetTracker(settings),
        )


def get_context(config: Any) -> GraphContext:
    configurable = config.get("configurable") if isinstance(config, dict) else None
    if not isinstance(configurable, dict) or "atlas" not in configurable:
        raise RuntimeError("GraphContext missing from runnable config")
    ctx = configurable["atlas"]
    if not isinstance(ctx, GraphContext):
        raise RuntimeError("invalid GraphContext")
    return ctx
