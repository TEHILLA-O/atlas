"""API request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from atlas.models.enums import HumanDecision


class ResearchCreateRequest(BaseModel):
    query: str = Field(min_length=8, max_length=8000)


class ResumeRequest(BaseModel):
    decision: HumanDecision = HumanDecision.APPROVE


class FeedbackRequest(BaseModel):
    research_id: str
    rating: int = Field(ge=1, le=5)
    comments: str = ""
    useful_sections: list[str] = Field(default_factory=list)
    flagged_errors: list[str] = Field(default_factory=list)


class MemoryCreateRequest(BaseModel):
    key: str
    value: str
    category: str = "preference"
    pinned: bool = False


class PaginatedDocuments(BaseModel):
    items: list[dict[str, Any]]
    limit: int
    offset: int
