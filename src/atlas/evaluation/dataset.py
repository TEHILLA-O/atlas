"""Gold research cases used by the evaluation suite."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvalCase:
    case_id: str
    query: str
    must_mention: list[str] = field(default_factory=list)
    forbidden_citations: list[str] = field(default_factory=list)
    expect_contradiction_topic: str | None = None
    minimum_evidence: int = 2


def load_dataset() -> list[EvalCase]:
    return [
        EvalCase(
            case_id="acme-public-sector",
            query=(
                "Analyse whether Acme Technology should enter the UK public-sector "
                "cybersecurity market."
            ),
            must_mention=["Cyber Essentials", "framework", "risk"],
            expect_contradiction_topic="revenue",
            minimum_evidence=3,
        ),
        EvalCase(
            case_id="supplier-compare",
            query="Compare five potential suppliers using uploaded documents and public information.",
            must_mention=["supplier", "risk"],
            minimum_evidence=1,
        ),
        EvalCase(
            case_id="source-disagreement",
            query="Analyse several reports and tell me where the sources disagree.",
            must_mention=["contradict"],
            expect_contradiction_topic="revenue",
            minimum_evidence=2,
        ),
    ]
