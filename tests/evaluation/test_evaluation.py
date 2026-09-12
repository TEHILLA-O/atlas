from __future__ import annotations

from atlas.evaluation.dataset import load_dataset
from atlas.evaluation.metrics import score_report
from atlas.evaluation.runner import _seed_evidence, run_evaluation
from atlas.models.confidence import ConfidenceAssessment
from atlas.models.contradiction import Contradiction
from atlas.models.enums import ContradictionSeverity
from atlas.models.evidence import Claim
from atlas.models.report import ResearchReport


def test_evaluation_suite_runs() -> None:
    report = run_evaluation()
    assert report.scores
    assert all(item.overall > 0 for item in report.scores)
    assert "Atlas evaluation" in report.summary()


def test_hallucinated_citation_is_penalised() -> None:
    case = load_dataset()[0]
    evidence = _seed_evidence()
    report = ResearchReport(
        research_id="x",
        title="t",
        executive_summary="s",
        research_question=case.query,
        recommendation="Enter via frameworks.",
        claims=[Claim(statement="Invented fact", evidence_ids=["nope"])],
        evidence=evidence,
        contradictions=[
            Contradiction(
                topic="annual revenue",
                claim_a="£15m",
                claim_b="£21m",
                evidence_a_id=evidence[1].evidence_id,
                evidence_b_id=evidence[2].evidence_id,
                severity=ContradictionSeverity.HIGH,
            )
        ],
        confidence=ConfidenceAssessment(
            overall=0.4,
            evidence_quality="LOW",
            source_agreement="LOW",
            coverage="LOW",
        ),
        markdown="risk framework cyber essentials",
    )
    score = score_report(case, report)
    assert score.hallucination_flags >= 1
    assert score.groundedness < 1
