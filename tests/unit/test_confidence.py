from __future__ import annotations

from atlas.models.contradiction import Contradiction
from atlas.models.enums import ContradictionSeverity, SourceQuality, SourceType
from atlas.models.evidence import Evidence
from atlas.services.confidence import assess_confidence


def _evidence(quality: SourceQuality, relevance: float = 0.8) -> Evidence:
    return Evidence(
        claim="x",
        quote_or_excerpt="Public-sector buyers require Cyber Essentials Plus.",
        source_type=SourceType.WEB,
        source_quality=quality,
        relevance_score=relevance,
        reliability_score=0.9,
        source_url="https://www.gov.uk/guidance",
    )


def test_confidence_drops_with_contradictions_and_gaps() -> None:
    high = assess_confidence(
        [_evidence(SourceQuality.GOVERNMENT), _evidence(SourceQuality.ACADEMIC)],
        [],
        [],
    )
    low = assess_confidence(
        [_evidence(SourceQuality.COMMUNITY, 0.2)],
        [
            Contradiction(
                topic="revenue",
                claim_a="£15m",
                claim_b="£21m",
                evidence_a_id="a",
                evidence_b_id="b",
                severity=ContradictionSeverity.HIGH,
            )
        ],
        ["missing contract value"],
    )
    assert high.overall > low.overall
    assert low.unresolved_contradictions == 1
    assert "decision-support" in high.rationale
