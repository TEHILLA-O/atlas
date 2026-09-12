"""Long-term memory items. Conversation history is never auto-promoted."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    key: str
    value: str
    category: str = "preference"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
    pinned: bool = False
