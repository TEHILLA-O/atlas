"""CRUD for research sessions, evidence, contradictions and reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.models.contradiction import Contradiction
from atlas.models.enums import ResearchStatus
from atlas.models.evidence import Evidence
from atlas.models.feedback import Feedback
from atlas.models.research import ResearchSession, ResearchTask
from atlas.persistence.orm import (
    ContradictionRow,
    EvidenceRow,
    FeedbackRow,
    ReportRow,
    ResearchSessionRow,
    ResearchTaskRow,
    UsageEventRow,
)


class ResearchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, query: str, thread_id: str) -> ResearchSession:
        row = ResearchSessionRow(
            user_query=query,
            status=ResearchStatus.CREATED.value,
            graph_thread_id=thread_id,
        )
        self.session.add(row)
        await self.session.flush()
        return self._to_session(row)

    async def get_session(self, research_id: str) -> ResearchSession | None:
        row = await self.session.get(ResearchSessionRow, research_id)
        return self._to_session(row) if row else None

    async def update_status(
        self,
        research_id: str,
        status: ResearchStatus,
        *,
        intent: str | None = None,
        iteration: int | None = None,
        confidence: float | None = None,
    ) -> None:
        row = await self.session.get(ResearchSessionRow, research_id)
        if row is None:
            return
        row.status = status.value
        row.updated_at = datetime.utcnow()
        if intent is not None:
            row.intent = intent
        if iteration is not None:
            row.iteration = iteration
        if confidence is not None:
            row.confidence_score = confidence

    async def replace_tasks(self, research_id: str, tasks: list[ResearchTask]) -> None:
        existing = await self.session.scalars(
            select(ResearchTaskRow).where(ResearchTaskRow.research_id == research_id)
        )
        for row in existing:
            await self.session.delete(row)
        for task in tasks:
            self.session.add(
                ResearchTaskRow(
                    id=task.id,
                    research_id=research_id,
                    question=task.question,
                    purpose=task.purpose,
                    source_types=[s.value for s in task.source_types],
                    priority=task.priority,
                    status=task.status,
                )
            )

    async def add_evidence(self, research_id: str, items: list[Evidence]) -> None:
        for item in items:
            self.session.add(
                EvidenceRow(
                    id=item.evidence_id,
                    research_id=research_id,
                    claim=item.claim,
                    source_url=item.source_url,
                    document_id=item.document_id,
                    quote_or_excerpt=item.quote_or_excerpt,
                    source_type=item.source_type.value,
                    relevance_score=item.relevance_score,
                    reliability_score=item.reliability_score,
                    source_quality=item.source_quality.value,
                    supports_claim=item.supports_claim,
                    extra=item.metadata,
                    retrieved_at=item.retrieved_at,
                )
            )

    async def list_evidence(self, research_id: str) -> list[Evidence]:
        rows = await self.session.scalars(
            select(EvidenceRow).where(EvidenceRow.research_id == research_id)
        )
        return [
            Evidence(
                evidence_id=row.id,
                claim=row.claim,
                source_url=row.source_url,
                document_id=row.document_id,
                quote_or_excerpt=row.quote_or_excerpt,
                source_type=row.source_type,  # type: ignore[arg-type]
                retrieved_at=row.retrieved_at,
                relevance_score=row.relevance_score,
                reliability_score=row.reliability_score,
                source_quality=row.source_quality,  # type: ignore[arg-type]
                supports_claim=row.supports_claim,
                metadata=row.extra or {},
            )
            for row in rows
        ]

    async def add_contradictions(
        self, research_id: str, items: list[Contradiction]
    ) -> None:
        for item in items:
            self.session.add(
                ContradictionRow(
                    id=item.id,
                    research_id=research_id,
                    topic=item.topic,
                    claim_a=item.claim_a,
                    claim_b=item.claim_b,
                    evidence_a_id=item.evidence_a_id,
                    evidence_b_id=item.evidence_b_id,
                    severity=item.severity.value,
                    possible_explanation=item.possible_explanation,
                    resolved=item.resolved,
                )
            )

    async def list_contradictions(self, research_id: str) -> list[Contradiction]:
        rows = await self.session.scalars(
            select(ContradictionRow).where(ContradictionRow.research_id == research_id)
        )
        return [
            Contradiction(
                id=row.id,
                topic=row.topic,
                claim_a=row.claim_a,
                claim_b=row.claim_b,
                evidence_a_id=row.evidence_a_id,
                evidence_b_id=row.evidence_b_id,
                severity=row.severity,  # type: ignore[arg-type]
                possible_explanation=row.possible_explanation,
                resolved=row.resolved,
            )
            for row in rows
        ]

    async def save_report(
        self, research_id: str, title: str, markdown: str, payload: dict[str, Any]
    ) -> str:
        row = ReportRow(
            research_id=research_id,
            title=title,
            markdown=markdown,
            payload=payload,
        )
        self.session.add(row)
        await self.session.flush()
        return row.id

    async def latest_report(self, research_id: str) -> ReportRow | None:
        result = await self.session.scalars(
            select(ReportRow)
            .where(ReportRow.research_id == research_id)
            .order_by(ReportRow.created_at.desc())
        )
        return result.first()

    async def add_feedback(self, feedback: Feedback) -> None:
        self.session.add(
            FeedbackRow(
                id=feedback.id,
                research_id=feedback.research_id,
                rating=feedback.rating,
                comments=feedback.comments,
                extra={
                    "useful_sections": feedback.useful_sections,
                    "flagged_errors": feedback.flagged_errors,
                },
            )
        )

    async def add_usage(
        self,
        research_id: str,
        node: str,
        *,
        model: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        latency_ms: float = 0.0,
    ) -> None:
        self.session.add(
            UsageEventRow(
                research_id=research_id,
                node=node,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                estimated_cost_usd=estimated_cost_usd,
                latency_ms=latency_ms,
            )
        )

    @staticmethod
    def _to_session(row: ResearchSessionRow) -> ResearchSession:
        return ResearchSession(
            id=row.id,
            user_query=row.user_query,
            intent=row.intent,  # type: ignore[arg-type]
            status=row.status,  # type: ignore[arg-type]
            iteration=row.iteration,
            confidence_score=row.confidence_score,
            created_at=row.created_at,
            updated_at=row.updated_at,
            metadata=row.extra or {},
        )
