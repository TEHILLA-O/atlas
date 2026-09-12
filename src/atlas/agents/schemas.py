"""Structured outputs produced by specialised agents."""

from __future__ import annotations

from pydantic import BaseModel, Field

from atlas.models.enums import ContradictionSeverity, IntentType, SourceType
from atlas.models.research import ResearchTask


class ClassificationResult(BaseModel):
    intent: IntentType
    high_impact: bool = False
    sensitive: bool = False
    rationale: str = ""


class ResearchPlan(BaseModel):
    tasks: list[ResearchTask] = Field(default_factory=list)


class QueryBundle(BaseModel):
    queries: list[str] = Field(default_factory=list)


class ExtractedEvidenceItem(BaseModel):
    claim: str
    quote_or_excerpt: str
    supports_claim: bool = True


class EvidenceExtraction(BaseModel):
    items: list[ExtractedEvidenceItem] = Field(default_factory=list)


class ContradictionDraft(BaseModel):
    topic: str
    claim_a: str
    claim_b: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    possible_explanation: str | None = None
    resolved: bool = False


class ContradictionAnalysis(BaseModel):
    items: list[ContradictionDraft] = Field(default_factory=list)


class GapAnalysisResult(BaseModel):
    unanswered_questions: list[str] = Field(default_factory=list)
    needs_another_pass: bool = False
    rationale: str = ""


class VerificationResult(BaseModel):
    unsupported_claims: list[str] = Field(default_factory=list)
    overstated_conclusions: list[str] = Field(default_factory=list)
    numeric_inconsistencies: list[str] = Field(default_factory=list)
    needs_more_research: bool = False
    notes: str = ""


class CriticResult(BaseModel):
    missing_evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    overweighted_sources: list[str] = Field(default_factory=list)
    reasoning_flaws: list[str] = Field(default_factory=list)
    confidence_too_high: bool = False
    summary: str = ""


class SynthesisResult(BaseModel):
    title: str
    executive_summary: str
    recommendation: str
    key_findings: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class QueryGenerationRequest(BaseModel):
    question: str
    source_types: list[SourceType] = Field(default_factory=list)
