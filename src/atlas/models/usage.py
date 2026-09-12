"""Token, cost and iteration accounting."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class UsageEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    research_id: str
    node: str
    model: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
