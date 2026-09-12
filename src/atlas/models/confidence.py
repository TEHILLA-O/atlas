"""Transparent decision-support confidence, not a calibrated probability."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConfidenceAssessment(BaseModel):
    """Explainable confidence derived from evidence quality and coverage."""

    overall: float = Field(ge=0.0, le=1.0)
    evidence_quality: str
    source_agreement: str
    coverage: str
    evidence_count: int = 0
    unresolved_contradictions: int = 0
    missing_information: list[str] = Field(default_factory=list)
    major_uncertainties: list[str] = Field(default_factory=list)
    rationale: str = ""

    def as_percent(self) -> int:
        return round(self.overall * 100)
