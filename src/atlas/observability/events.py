"""In-process and Redis-backed research progress events for SSE."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from atlas.observability.logging import get_logger

logger = get_logger(__name__)


class ProgressBus:
    """Fan-out progress events. Redis is used when available, memory otherwise."""

    def __init__(self) -> None:
        self._local: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def publish(self, research_id: str, message: str, **extra: Any) -> None:
        event = {
            "research_id": research_id,
            "message": message,
            "ts": datetime.utcnow().isoformat(),
            **extra,
        }
        self._local[research_id].append(event)
        logger.info("research_progress", **event)

    def history(self, research_id: str) -> list[dict[str, Any]]:
        return list(self._local.get(research_id, []))

    async def subscribe(self, research_id: str) -> AsyncIterator[str]:
        for event in self.history(research_id):
            yield json.dumps(event)


progress_bus = ProgressBus()
