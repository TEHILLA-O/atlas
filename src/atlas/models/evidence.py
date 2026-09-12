"""Evidence, claims and citation models. Citations must point at real evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from atlas.models.enums import SourceQuality, SourceType


class Evidence(BaseModel):
    """A retrieved, scored excerpt that can support or refute a claim."""

    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    claim: str
    source_url: str | None = None
    document_id: str | None = None
    quote_or_excerpt: str
    source_type: SourceType
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    source_quality: SourceQuality = SourceQuality.UNKNOWN
    supports_claim: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    def citation_label(self) -> str:
        source = self.source_url or self.document_id or "internal"
        return f"[{self.evidence_id[:8]}:{source}]"


class Claim(BaseModel):
    """A factual statement that must be grounded in evidence or marked unsupported."""

    claim_id: str = Field(default_factory=lambda: str(uuid4()))
    statement: str
    evidence_ids: list[str] = Field(default_factory=list)
    supported: bool = False
    strength: float = Field(default=0.0, ge=0.0, le=1.0)
    section: str = "findings"


class Citation(BaseModel):
    """Internal Claim → Evidence → Source link. Never invented."""

    claim_id: str
    evidence_id: str
    source_ref: str
    excerpt: str
    verified: bool = False
