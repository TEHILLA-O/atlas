"""LangGraph node implementations. Each node mutates structured state only."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig

from atlas.graph.context import get_context
from atlas.graph.state import ResearchState
from atlas.models.contradiction import Contradiction
from atlas.models.enums import ResearchStatus, SourceType
from atlas.models.evidence import Evidence
from atlas.models.research import ResearchTask
from atlas.observability.events import progress_bus
from atlas.services.confidence import assess_confidence
from atlas.services.contradictions import detect_contradictions


def _ctx(config: RunnableConfig) -> Any:
    return get_context(config)


async def classify_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    result = await ctx.planner.classify(state["user_query"])
    await progress_bus.publish(state["research_id"], "Classified research request.", intent=result.intent.value)
    return {
        "intent": result.intent.value,
        "high_impact": result.high_impact,
        "sensitive": result.sensitive,
        "status": ResearchStatus.CLASSIFYING.value,
        "progress": [f"Intent classified as {result.intent.value}."],
    }


async def plan_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    ctx.budget.begin_iteration()
    tasks = await ctx.planner.plan(state["user_query"], state.get("intent", "general_research"))
    await progress_bus.publish(
        state["research_id"],
        f"{len(tasks)} research tasks created.",
        tasks=len(tasks),
    )
    return {
        "research_plan": [task.model_dump(mode="json") for task in tasks],
        "iteration": ctx.budget.iterations,
        "status": ResearchStatus.PLANNING.value,
        "needs_more_research": False,
        "progress": [f"{len(tasks)} research tasks created."],
    }


async def research_task_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    raw_task = state.get("current_task") or {}
    task = ResearchTask.model_validate(raw_task)
    queries = await ctx.planner.queries_for(task)
    evidence: list[Evidence] = []
    results = []
    source_types = set(task.source_types)
    if SourceType.WEB in source_types or not source_types:
        await progress_bus.publish(state["research_id"], f"Researching publicly: {task.question}")
        web_result, web_evidence = await ctx.researcher.run(task, queries)
        results.append(web_result)
        evidence.extend(web_evidence)
    if SourceType.DOCUMENT in source_types or not source_types:
        await progress_bus.publish(state["research_id"], f"Searching uploaded documents: {task.question}")
        doc_result, doc_evidence = await ctx.document_analyst.run(task)
        results.append(doc_result)
        evidence.extend(doc_evidence)
    ctx.budget.record(node="research_task", sources=len(evidence))
    completed = [item.model_dump(mode="json") for item in results]
    return {
        "completed_tasks": completed,
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "status": ResearchStatus.RESEARCHING.value,
        "sources_reviewed": len(evidence),
        "progress": [f"Completed task: {task.question}"],
    }


async def analyse_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    evidence = [Evidence.model_validate(item) for item in state.get("evidence", [])]
    await progress_bus.publish(
        state["research_id"],
        f"{len(evidence)} evidence items collected.",
        evidence=len(evidence),
    )
    contradictions = await detect_contradictions(evidence, ctx.llm)
    unanswered = _gaps(state.get("research_plan", []), evidence)
    needs_pass = bool(unanswered) and ctx.budget.can_iterate() and not ctx.budget.exceeded()
    if state.get("iteration", 1) >= ctx.settings.max_iterations:
        needs_pass = False
    await progress_bus.publish(
        state["research_id"],
        f"Checking contradictions... {len(contradictions)} found.",
    )
    return {
        "contradictions": [item.model_dump(mode="json") for item in contradictions],
        "unanswered_questions": unanswered,
        "needs_more_research": needs_pass and state.get("iteration", 1) < ctx.settings.max_iterations,
        "status": ResearchStatus.ANALYSING.value,
        "progress": [
            f"{len(evidence)} evidence items collected.",
            f"{len(contradictions)} contradictions identified.",
        ],
    }


async def synthesise_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    evidence = [Evidence.model_validate(item) for item in state.get("evidence", [])]
    contradictions = [Contradiction.model_validate(item) for item in state.get("contradictions", [])]
    confidence = assess_confidence(
        evidence, contradictions, state.get("unanswered_questions", [])
    )
    await progress_bus.publish(state["research_id"], "Drafting report...")
    report = await ctx.synthesizer.synthesise(
        research_id=state["research_id"],
        query=state["user_query"],
        evidence=evidence,
        contradictions=contradictions,
        gaps=state.get("unanswered_questions", []),
        confidence=confidence,
        critic_notes=[],
    )
    return {
        "confidence": confidence.model_dump(mode="json"),
        "confidence_score": confidence.overall,
        "draft_report": report.markdown,
        "report": report.model_dump(mode="json"),
        "status": ResearchStatus.SYNTHESISING.value,
        "progress": ["Draft report produced."],
    }


async def verify_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    from atlas.models.evidence import Claim

    report = state.get("report") or {}
    claims = [Claim.model_validate(item) for item in report.get("claims", [])]
    evidence = [Evidence.model_validate(item) for item in state.get("evidence", [])]
    result = await ctx.verifier.verify(state.get("draft_report") or "", claims, evidence)
    needs = result.needs_more_research and ctx.budget.can_iterate() and not ctx.budget.exceeded()
    await progress_bus.publish(state["research_id"], "Verification complete.")
    return {
        "verification": result.model_dump(mode="json"),
        "needs_more_research": needs,
        "status": ResearchStatus.VERIFYING.value,
        "progress": ["Fact and citation verification complete."],
    }


async def critic_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    evidence = [Evidence.model_validate(item) for item in state.get("evidence", [])]
    contradictions = [Contradiction.model_validate(item) for item in state.get("contradictions", [])]
    result = await ctx.critic.critique(state.get("draft_report") or "", evidence, contradictions)
    report = dict(state.get("report") or {})
    report["critic_notes"] = [
        result.summary,
        *[f"Assumption: {item}" for item in result.assumptions],
        *[f"Missing: {item}" for item in result.missing_evidence],
    ]
    return {
        "critic": result.model_dump(mode="json"),
        "report": report,
        "progress": ["Critic review complete."],
    }


async def human_review_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    decision = state.get("human_decision")
    needs = ctx.settings.hitl_enabled and _requires_human(state, ctx.settings)
    payload = {
        "confidence": state.get("confidence_score", 0.0),
        "contradictions": len(state.get("contradictions", [])),
        "question": "Research complete. Continue with the recommendation?",
        "options": ["approve", "request_more_research", "cancel"],
    }
    if ctx.settings.env == "test":
        return {
            "human_decision": str(decision or "approve"),
            "interrupt_payload": None,
            "progress": ["Human review auto-approved in test environment."],
        }
    if needs and not decision:
        try:
            from langgraph.types import interrupt

            decision = interrupt(payload)
        except Exception:
            return {
                "status": ResearchStatus.AWAITING_HUMAN.value,
                "interrupt_payload": payload,
                "progress": ["Awaiting human review."],
            }
    return {
        "human_decision": str(decision) if decision else "approve",
        "interrupt_payload": payload if needs else None,
        "status": ResearchStatus.AWAITING_HUMAN.value
        if needs and not decision
        else state.get("status", ResearchStatus.VERIFYING.value),
        "progress": [f"Human decision: {decision or 'auto-approve'}."],
    }


async def finalise_node(state: ResearchState, config: RunnableConfig) -> dict[str, Any]:
    report = dict(state.get("report") or {})
    markdown = state.get("draft_report") or ""
    decision = state.get("human_decision") or "approve"
    if decision == "cancel":
        return {
            "status": ResearchStatus.CANCELLED.value,
            "final_report": None,
            "progress": ["Research cancelled by reviewer."],
        }
    await progress_bus.publish(state["research_id"], "Final report ready.")
    return {
        "final_report": markdown,
        "report": report,
        "status": ResearchStatus.COMPLETED.value,
        "budget": _ctx(config).budget.snapshot(),
        "progress": ["Final report ready."],
    }


def _gaps(plan: list[dict[str, Any]], evidence: list[Evidence]) -> list[str]:
    if not plan:
        return []
    covered = " ".join(item.quote_or_excerpt.lower() for item in evidence)
    missing: list[str] = []
    for task in plan:
        tokens = [token for token in str(task.get("question", "")).lower().split() if len(token) > 4]
        if tokens and sum(1 for token in tokens if token in covered) / len(tokens) < 0.15:
            missing.append(str(task.get("question")))
    return missing[:5]


def _requires_human(state: ResearchState, settings: Any) -> bool:
    score = float(state.get("confidence_score") or 0)
    unresolved = [
        item
        for item in state.get("contradictions", [])
        if not item.get("resolved")
    ]
    return bool(
        score < settings.hitl_low_confidence
        or (settings.hitl_high_impact and state.get("high_impact"))
        or len(unresolved) >= 2
    )
