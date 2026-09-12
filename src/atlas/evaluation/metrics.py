"""Deterministic evaluation metrics. LLM-as-judge is optional and secondary."""

from __future__ import annotations

from dataclasses import dataclass

from atlas.evaluation.dataset import EvalCase
from atlas.models.report import ResearchReport
from atlas.rag.citations import find_unsupported_claims


@dataclass(slots=True)
class CaseScore:
    case_id: str
    groundedness: float
    citation_correctness: float
    coverage: float
    contradiction_detected: bool
    hallucination_flags: int
    usefulness: float

    @property
    def overall(self) -> float:
        return round(
            (
                self.groundedness
                + self.citation_correctness
                + self.coverage
                + self.usefulness
                + (1.0 if self.contradiction_detected else 0.6)
            )
            / 5,
            3,
        )


def score_report(case: EvalCase, report: ResearchReport) -> CaseScore:
    unsupported = find_unsupported_claims(report.claims)
    groundedness = 1.0 - min(1.0, len(unsupported) / max(1, len(report.claims) or 1))
    verified = [item for item in report.citations if item.verified]
    citation_correctness = (
        len(verified) / len(report.citations) if report.citations else 0.0
    )
    haystack = report.markdown.lower()
    hits = sum(1 for token in case.must_mention if token.lower() in haystack)
    coverage = hits / len(case.must_mention) if case.must_mention else 1.0
    contradiction = True
    if case.expect_contradiction_topic:
        contradiction = any(
            case.expect_contradiction_topic.lower() in item.topic.lower()
            or case.expect_contradiction_topic.lower() in item.claim_a.lower()
            or case.expect_contradiction_topic.lower() in item.claim_b.lower()
            for item in report.contradictions
        )
    fake = [
        item
        for item in report.citations
        if any(bad in item.source_ref for bad in case.forbidden_citations)
    ]
    usefulness = 1.0 if report.recommendation and report.executive_summary else 0.3
    if len(report.evidence) < case.minimum_evidence:
        usefulness *= 0.5
    return CaseScore(
        case_id=case.case_id,
        groundedness=round(groundedness, 3),
        citation_correctness=round(citation_correctness, 3),
        coverage=round(coverage, 3),
        contradiction_detected=contradiction,
        hallucination_flags=len(unsupported) + len(fake),
        usefulness=round(usefulness, 3),
    )
