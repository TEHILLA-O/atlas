"""Structured research report consumed by API, UI and exporters."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from atlas.models.confidence import ConfidenceAssessment
from atlas.models.contradiction import Contradiction
from atlas.models.evidence import Citation, Claim, Evidence


class ResearchReport(BaseModel):
    """Canonical report object. Markdown/JSON are projections of this model."""

    report_id: str = Field(default_factory=lambda: str(uuid4()))
    research_id: str
    title: str
    executive_summary: str
    research_question: str
    recommendation: str
    key_findings: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    confidence: ConfidenceAssessment
    sources: list[str] = Field(default_factory=list)
    critic_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
    markdown: str = ""
