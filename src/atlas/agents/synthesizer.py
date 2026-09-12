"""Synthesiser: structured report grounded in evidence IDs."""

from __future__ import annotations

from atlas.agents.schemas import SynthesisResult
from atlas.llm.factory import LLMClient
from atlas.models.confidence import ConfidenceAssessment
from atlas.models.contradiction import Contradiction
from atlas.models.evidence import Citation, Claim, Evidence
from atlas.models.report import ResearchReport
from atlas.prompts.templates import SYNTHESISER_SYSTEM
from atlas.rag.citations import map_citations
from atlas.services.reporting import render_markdown


class SynthesizerAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def synthesise(
        self,
        *,
        research_id: str,
        query: str,
        evidence: list[Evidence],
        contradictions: list[Contradiction],
        gaps: list[str],
        confidence: ConfidenceAssessment,
        critic_notes: list[str],
    ) -> ResearchReport:
        prompt = (
            f"Question: {query}\nEvidence:\n"
            + "\n".join(
                f"- {item.evidence_id}: {item.quote_or_excerpt[:280]}" for item in evidence[:20]
            )
            + f"\nGaps: {gaps}\nContradictions: {[c.topic for c in contradictions]}"
        )
        result = await self.llm.structured(prompt, SynthesisResult, system=SYNTHESISER_SYSTEM)
        assert isinstance(result, SynthesisResult)
        claims = [
            Claim(statement=finding, evidence_ids=_match_evidence(finding, evidence), section="findings")
            for finding in result.key_findings
        ]
        citations: list[Citation] = map_citations(claims, evidence)
        sources = sorted(
            {
                item.source_url or item.document_id or "internal"
                for item in evidence
                if item.source_url or item.document_id
            }
        )
        report = ResearchReport(
            research_id=research_id,
            title=result.title,
            executive_summary=result.executive_summary,
            research_question=query,
            recommendation=result.recommendation,
            key_findings=result.key_findings,
            opportunities=result.opportunities,
            risks=result.risks,
            unknowns=result.unknowns + gaps,
            claims=claims,
            citations=citations,
            evidence=evidence,
            contradictions=contradictions,
            confidence=confidence,
            sources=sources,
            critic_notes=critic_notes,
        )
        report.markdown = render_markdown(report)
        return report


def _match_evidence(statement: str, evidence: list[Evidence]) -> list[str]:
    tokens = {token.lower() for token in statement.split() if len(token) > 3}
    matched: list[str] = []
    for item in evidence:
        hay = item.quote_or_excerpt.lower()
        if tokens and sum(1 for token in tokens if token in hay) / len(tokens) >= 0.2:
            matched.append(item.evidence_id)
    return matched[:3]
