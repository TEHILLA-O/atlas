"""Transparent decision-support confidence. Not a calibrated probability."""

from __future__ import annotations

from atlas.models.confidence import ConfidenceAssessment
from atlas.models.contradiction import Contradiction
from atlas.models.enums import SourceQuality
from atlas.models.evidence import Evidence
from atlas.rag.source_quality import QUALITY_WEIGHTS


def assess_confidence(
    evidence: list[Evidence],
    contradictions: list[Contradiction],
    unanswered: list[str],
) -> ConfidenceAssessment:
    if not evidence:
        return ConfidenceAssessment(
            overall=0.15,
            evidence_quality="LOW",
            source_agreement="UNKNOWN",
            coverage="LOW",
            evidence_count=0,
            unresolved_contradictions=len(contradictions),
            missing_information=unanswered,
            major_uncertainties=["No evidence was retrieved."],
            rationale="Confidence is low because the run produced no evidence.",
        )

    quality_score = sum(QUALITY_WEIGHTS.get(item.source_quality, 0.4) for item in evidence) / len(
        evidence
    )
    relevance = sum(item.relevance_score for item in evidence) / len(evidence)
    unresolved = [item for item in contradictions if not item.resolved]
    agreement = 1.0 - min(0.7, 0.18 * len(unresolved))
    coverage = max(0.2, 1.0 - 0.12 * len(unanswered))
    overall = max(
        0.05,
        min(
            0.95,
            0.35 * quality_score + 0.25 * relevance + 0.25 * agreement + 0.15 * coverage,
        ),
    )
    quality_label = _band(quality_score)
    agreement_label = "LOW" if unresolved else _band(agreement)
    coverage_label = _band(coverage)
    uncertainties = [f"Unresolved contradiction: {item.topic}" for item in unresolved]
    uncertainties.extend(unanswered[:3])
    if not any(item.source_quality in {SourceQuality.GOVERNMENT, SourceQuality.PRIMARY} for item in evidence):
        uncertainties.append("No primary or government source was retrieved.")
    return ConfidenceAssessment(
        overall=round(overall, 2),
        evidence_quality=quality_label,
        source_agreement=agreement_label,
        coverage=coverage_label,
        evidence_count=len(evidence),
        unresolved_contradictions=len(unresolved),
        missing_information=unanswered,
        major_uncertainties=uncertainties[:6],
        rationale=(
            f"Score combines evidence quality ({quality_label}), source agreement "
            f"({agreement_label}) and coverage ({coverage_label}). "
            "This is a decision-support metric, not a statistical probability."
        ),
    )


def _band(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    if score >= 0.5:
        return "MEDIUM"
    return "LOW"
