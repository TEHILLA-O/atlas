"""Run evaluation cases against the demo pipeline without live vendors."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from atlas.agents.synthesizer import SynthesizerAgent
from atlas.config.settings import Settings
from atlas.evaluation.dataset import load_dataset
from atlas.evaluation.metrics import CaseScore, score_report
from atlas.llm.providers.demo import DemoLLM
from atlas.models.enums import SourceQuality, SourceType
from atlas.models.evidence import Evidence
from atlas.services.confidence import assess_confidence
from atlas.services.contradictions import detect_contradictions


@dataclass
class EvaluationReport:
    scores: list[CaseScore]

    def summary(self) -> str:
        if not self.scores:
            return "No evaluation cases."
        avg = sum(item.overall for item in self.scores) / len(self.scores)
        lines = [f"Atlas evaluation: {len(self.scores)} cases, mean score {avg:.2f}"]
        for item in self.scores:
            lines.append(
                f"- {item.case_id}: overall={item.overall} grounded={item.groundedness} "
                f"citations={item.citation_correctness} coverage={item.coverage} "
                f"contradiction={item.contradiction_detected} hallucinations={item.hallucination_flags}"
            )
        return "\n".join(lines)


def run_evaluation() -> EvaluationReport:
    return asyncio.run(_run())


async def _run() -> EvaluationReport:
    llm = DemoLLM()
    synthesizer = SynthesizerAgent(llm)
    scores: list[CaseScore] = []
    for case in load_dataset():
        evidence = _seed_evidence()
        contradictions = await detect_contradictions(evidence, llm)
        confidence = assess_confidence(evidence, contradictions, [])
        report = await synthesizer.synthesise(
            research_id="eval",
            query=case.query,
            evidence=evidence,
            contradictions=contradictions,
            gaps=[],
            confidence=confidence,
            critic_notes=["Evaluation critic placeholder."],
        )
        scores.append(score_report(case, report))
    return EvaluationReport(scores=scores)


def _seed_evidence() -> list[Evidence]:
    return [
        Evidence(
            claim="Public-sector buyers require Cyber Essentials Plus.",
            source_url="https://www.ncsc.gov.uk/cyberessentials/overview",
            quote_or_excerpt=(
                "Cyber Essentials Plus is commonly required as a tender gate "
                "for UK public-sector cybersecurity contracts."
            ),
            source_type=SourceType.WEB,
            relevance_score=0.9,
            reliability_score=0.95,
            source_quality=SourceQuality.GOVERNMENT,
        ),
        Evidence(
            claim="Acme revenue",
            document_id="memo-1",
            quote_or_excerpt="Internal briefing states Acme Technology annual revenue was £15m.",
            source_type=SourceType.DOCUMENT,
            relevance_score=0.8,
            reliability_score=0.7,
            source_quality=SourceQuality.COMPANY_SOURCE,
        ),
        Evidence(
            claim="Acme revenue public",
            source_url="https://news.example.com/acme-revenue-thread",
            quote_or_excerpt="Commenters claim Acme Technology annual revenue was £21m last year.",
            source_type=SourceType.WEB,
            relevance_score=0.6,
            reliability_score=0.35,
            source_quality=SourceQuality.COMMUNITY,
        ),
        Evidence(
            claim="Frameworks dominate",
            source_url="https://www.gartner.com/en/documents/uk-public-cyber",
            quote_or_excerpt="Framework agreements remain the dominant route to market for specialist suppliers.",
            source_type=SourceType.WEB,
            relevance_score=0.85,
            reliability_score=0.65,
            source_quality=SourceQuality.INDUSTRY,
        ),
    ]


def settings_for_eval() -> Settings:
    return Settings.model_validate({"ATLAS_ENV": "test", "MODEL_PROVIDER": "demo"})
