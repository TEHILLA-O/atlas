"""Research session, task and result models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from atlas.models.enums import IntentType, ResearchStatus, SourceType, TaskPriority


class ResearchTask(BaseModel):
    """A planner-generated subtask with least-privilege source constraints."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    purpose: str
    source_types: list[SourceType] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1, le=10)
    priority_label: TaskPriority = TaskPriority.MEDIUM
    depends_on: list[str] = Field(default_factory=list)
    status: str = "pending"


class ResearchResult(BaseModel):
    """Outcome of executing a single research task."""

    task_id: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    sources_consulted: int = 0
    errors: list[str] = Field(default_factory=list)
    completed: bool = True


class ResearchSession(BaseModel):
    """Persistent research engagement owned by the API layer."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_query: str
    intent: IntentType | None = None
    status: ResearchStatus = ResearchStatus.CREATED
    iteration: int = 0
    confidence_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
