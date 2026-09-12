"""Structured contradiction records produced by the contradiction detector."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from atlas.models.enums import ContradictionSeverity


class Contradiction(BaseModel):
    """Two pieces of evidence that cannot both be true without explanation."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    claim_a: str
    claim_b: str
    evidence_a_id: str
    evidence_b_id: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    possible_explanation: str | None = None
    resolved: bool = False
    resolution_notes: str | None = None
