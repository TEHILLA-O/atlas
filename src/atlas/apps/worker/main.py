"""Worker process used for long-running research in deployed environments."""

from __future__ import annotations

import asyncio

from atlas.config.settings import get_settings
from atlas.observability.logging import configure_logging, get_logger
from atlas.observability.tracing import configure_langsmith

logger = get_logger(__name__)


async def _loop() -> None:
    settings = get_settings()
    configure_logging(settings)
    configure_langsmith(settings)
    logger.info("atlas_worker_idle", note="API currently runs research in-process in demo mode.")
    while True:
        await asyncio.sleep(30)


def run() -> None:
    asyncio.run(_loop())
