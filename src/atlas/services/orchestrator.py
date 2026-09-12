"""Run, resume and cancel research graphs with durable thread IDs."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.config.settings import Settings
from atlas.graph.context import GraphContext
from atlas.graph.workflow import compile_research_graph
from atlas.models.enums import HumanDecision, ResearchStatus
from atlas.observability.events import progress_bus
from atlas.observability.logging import get_logger
from atlas.repositories.research_repository import ResearchRepository
from atlas.services.runtime import Runtime

logger = get_logger(__name__)

_memory_saver = MemorySaver()
_compiled = compile_research_graph(_memory_saver)


class ResearchOrchestrator:
    def __init__(self, session: AsyncSession, settings: Settings, runtime: Runtime) -> None:
        self.session = session
        self.settings = settings
        self.runtime = runtime
        self.repo = ResearchRepository(session)

    async def start(self, query: str) -> dict[str, Any]:
        research_id = str(uuid4())
        await self.repo.create_session(query, thread_id=research_id)
        await self.session.commit()
        await progress_bus.publish(research_id, "Planning research...")
        context = GraphContext.build(self.settings, self.runtime.llm, self.runtime.tools)
        config = {
            "configurable": {"thread_id": research_id, "atlas": context},
            "run_name": "atlas.research",
        }
        initial = {
            "research_id": research_id,
            "user_query": query,
            "iteration": 0,
            "status": ResearchStatus.CREATED.value,
            "completed_tasks": [],
            "evidence": [],
            "errors": [],
            "progress": ["Planning research..."],
            "sources_reviewed": 0,
        }
        try:
            result = await _compiled.ainvoke(initial, config=config)
        except Exception as exc:
            if "Interrupt" in type(exc).__name__:
                snap = await _compiled.aget_state(config)
                result = dict(snap.values) if snap and snap.values else initial
                result["status"] = ResearchStatus.AWAITING_HUMAN.value
            else:
                logger.exception("research_failed", research_id=research_id)
                await self.repo.update_status(research_id, ResearchStatus.FAILED)
                await self.session.commit()
                raise RuntimeError(f"research failed: {exc}") from exc
        await self._persist_result(research_id, result, context)
        return {"research_id": research_id, **_public(result)}

    async def resume(self, research_id: str, decision: HumanDecision) -> dict[str, Any]:
        context = GraphContext.build(self.settings, self.runtime.llm, self.runtime.tools)
        config = {"configurable": {"thread_id": research_id, "atlas": context}}
        result = await _compiled.ainvoke(
            {"human_decision": decision.value},
            config=config,
        )
        await self._persist_result(research_id, result, context)
        return {"research_id": research_id, **_public(result)}

    async def cancel(self, research_id: str) -> None:
        await self.repo.update_status(research_id, ResearchStatus.CANCELLED)
        await self.session.commit()
        await progress_bus.publish(research_id, "Research cancelled.")

    async def snapshot(self, research_id: str) -> dict[str, Any] | None:
        config = {"configurable": {"thread_id": research_id}}
        snap = await _compiled.aget_state(config)
        if snap is None or not snap.values:
            session = await self.repo.get_session(research_id)
            return session.model_dump(mode="json") if session else None
        return _public(dict(snap.values))

    async def _persist_result(
        self,
        research_id: str,
        result: dict[str, Any],
        context: GraphContext,
    ) -> None:
        from atlas.models.contradiction import Contradiction
        from atlas.models.enums import ResearchStatus as Status
        from atlas.models.evidence import Evidence
        from atlas.models.research import ResearchTask

        status = Status(result.get("status", Status.COMPLETED.value))
        await self.repo.update_status(
            research_id,
            status,
            intent=result.get("intent"),
            iteration=result.get("iteration"),
            confidence=result.get("confidence_score"),
        )
        plan = [ResearchTask.model_validate(item) for item in result.get("research_plan", [])]
        if plan:
            await self.repo.replace_tasks(research_id, plan)
        evidence = [Evidence.model_validate(item) for item in result.get("evidence", [])]
        if evidence:
            await self.repo.add_evidence(research_id, evidence)
        contradictions = [
            Contradiction.model_validate(item) for item in result.get("contradictions", [])
        ]
        if contradictions:
            await self.repo.add_contradictions(research_id, contradictions)
        if result.get("final_report"):
            await self.repo.save_report(
                research_id,
                (result.get("report") or {}).get("title", "Atlas report"),
                result["final_report"],
                result.get("report") or {},
            )
        snap = context.budget.snapshot()
        await self.repo.add_usage(
            research_id,
            "workflow",
            model=self.runtime.llm.model,
            prompt_tokens=int(snap["tokens_used"]),
            estimated_cost_usd=float(snap["cost_usd"]),
        )
        await self.session.commit()


def _public(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "intent": result.get("intent"),
        "iteration": result.get("iteration"),
        "confidence_score": result.get("confidence_score"),
        "progress": result.get("progress", []),
        "research_plan": result.get("research_plan", []),
        "evidence": result.get("evidence", []),
        "contradictions": result.get("contradictions", []),
        "unanswered_questions": result.get("unanswered_questions", []),
        "confidence": result.get("confidence"),
        "final_report": result.get("final_report"),
        "report": result.get("report"),
        "interrupt_payload": result.get("interrupt_payload"),
        "budget": result.get("budget"),
    }
