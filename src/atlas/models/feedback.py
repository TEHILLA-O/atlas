"""Human feedback captured after a research run."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    research_id: str
    rating: int = Field(ge=1, le=5)
    comments: str = ""
    useful_sections: list[str] = Field(default_factory=list)
    flagged_errors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
