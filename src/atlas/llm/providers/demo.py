"""Deterministic demo LLM so Atlas can run and be tested without vendor keys."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from atlas.models.enums import IntentType, SourceType


class DemoLLM:
    """Structured-output stub used in tests, CI and local demos."""

    provider = "demo"

    def __init__(self, model: str = "demo-atlas") -> None:
        self.model = model

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        lowered = prompt.lower()
        if "executive summary" in lowered or "draft a report" in lowered:
            return (
                "Acme Technology has a credible but constrained path into the UK "
                "public-sector cybersecurity market. The strongest opportunity is "
                "framework-based supply rather than prime-contractor bids."
            )
        if "critic" in lowered or "attack the reasoning" in lowered:
            return (
                "The recommendation assumes Cyber Essentials Plus can be obtained "
                "quickly. Contract values in public notes and the company memo disagree."
            )
        return "Demo completion: evidence assembled from local documents and curated sources."

    async def structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
    ) -> BaseModel:
        name = schema.__name__
        payload = _payload_for(name, prompt)
        return schema.model_validate(payload)


def _payload_for(schema_name: str, prompt: str) -> dict[str, Any]:
    query = prompt.lower()
    if schema_name == "ClassificationResult":
        intent = IntentType.GENERAL_RESEARCH
        if "public-sector" in query or "opportunity" in query:
            intent = IntentType.OPPORTUNITY_ASSESSMENT
        elif "supplier" in query or "compare" in query:
            intent = IntentType.SUPPLIER_COMPARISON
        elif "due diligence" in query or "investigate" in query:
            intent = IntentType.DUE_DILIGENCE
        elif "disagree" in query or "contradict" in query:
            intent = IntentType.CONTRADICTION_ANALYSIS
        elif "market" in query:
            intent = IntentType.MARKET_ANALYSIS
        high_impact = intent in {
            IntentType.OPPORTUNITY_ASSESSMENT,
            IntentType.DUE_DILIGENCE,
        }
        return {
            "intent": intent.value,
            "high_impact": high_impact,
            "sensitive": False,
            "rationale": "Demo classifier mapped keywords onto a research intent.",
        }
    if schema_name == "ResearchPlan":
        return {
            "tasks": [
                {
                    "question": "What is the size and growth of the UK public-sector cybersecurity market?",
                    "purpose": "Quantify market opportunity.",
                    "source_types": [SourceType.WEB.value, SourceType.DOCUMENT.value],
                    "priority": 1,
                },
                {
                    "question": "What procurement and accreditation barriers apply?",
                    "purpose": "Identify eligibility and entry barriers.",
                    "source_types": [SourceType.WEB.value, SourceType.DOCUMENT.value],
                    "priority": 1,
                },
                {
                    "question": "Who are the major incumbents and how do they compete?",
                    "purpose": "Map competitive landscape.",
                    "source_types": [SourceType.WEB.value, SourceType.DOCUMENT.value],
                    "priority": 2,
                },
                {
                    "question": "What capabilities and commercial constraints does Acme have?",
                    "purpose": "Assess internal fitness using uploaded documents.",
                    "source_types": [SourceType.DOCUMENT.value],
                    "priority": 1,
                },
                {
                    "question": "What are the principal delivery, compliance and commercial risks?",
                    "purpose": "Surface material risks before recommendation.",
                    "source_types": [SourceType.DOCUMENT.value, SourceType.WEB.value],
                    "priority": 2,
                },
            ]
        }
    if schema_name == "QueryBundle":
        return {
            "queries": [
                "UK public sector cybersecurity procurement frameworks",
                "Cyber Essentials Plus public sector requirement",
                "Acme Technology capabilities and revenue",
            ]
        }
    if schema_name == "EvidenceExtraction":
        return {
            "items": [
                {
                    "claim": "UK public bodies commonly require Cyber Essentials Plus.",
                    "quote_or_excerpt": "Buyers typically require Cyber Essentials Plus for relevant contracts.",
                    "supports_claim": True,
                }
            ]
        }
    if schema_name == "ContradictionAnalysis":
        return {
            "items": [
                {
                    "topic": "Annual revenue",
                    "claim_a": "Company revenue was £15m.",
                    "claim_b": "Company revenue was £21m.",
                    "severity": "high",
                    "possible_explanation": "Different reporting periods or management vs statutory figures.",
                    "resolved": False,
                }
            ]
        }
    if schema_name == "GapAnalysisResult":
        return {
            "unanswered_questions": [
                "Independently confirmed current-year contract value.",
            ],
            "needs_another_pass": False,
            "rationale": "Core eligibility and market questions are covered; remaining gaps are commercial confirmation.",
        }
    if schema_name == "VerificationResult":
        return {
            "unsupported_claims": [],
            "overstated_conclusions": [],
            "numeric_inconsistencies": [],
            "needs_more_research": False,
            "notes": "Demo verifier found citations that match retrieved excerpts.",
        }
    if schema_name == "CriticResult":
        return {
            "missing_evidence": [
                "Independent confirmation of Acme's latest audited revenue.",
            ],
            "assumptions": [
                "Cyber Essentials Plus can be obtained within one procurement cycle.",
            ],
            "alternative_explanations": [
                "Revenue figures may describe different legal entities.",
            ],
            "overweighted_sources": [
                "Internal company memo versus official government guidance.",
            ],
            "reasoning_flaws": [
                "Correlation between market growth and Acme win-rate is unproven.",
            ],
            "confidence_too_high": False,
            "summary": "The recommendation is directionally sound but commercially under-evidenced.",
        }
    if schema_name == "SynthesisResult":
        return {
            "title": "Acme Technology — UK public-sector cybersecurity entry",
            "executive_summary": (
                "Acme should pursue the market as a specialist subcontractor on established "
                "frameworks rather than as a first-time prime bidder."
            ),
            "recommendation": (
                "Enter via G-Cloud / framework supply with Cyber Essentials Plus as a "
                "gate, while resolving the revenue contradiction before material bids."
            ),
            "key_findings": [
                "Public-sector buyers treat Cyber Essentials Plus as a common gate.",
                "Internal documents and public notes disagree on Acme revenue.",
                "Incumbents win through framework presence more than standalone tenders.",
            ],
            "opportunities": [
                "Specialist SOC and incident-response subcontracting.",
                "Niche support for smaller public bodies.",
            ],
            "risks": [
                "Accreditation delay.",
                "Unresolved financial inconsistency in source documents.",
                "Incumbent framework lock-in.",
            ],
            "unknowns": [
                "Independently confirmed contract values.",
            ],
        }
    empty: dict[str, Any] = {}
    return empty
