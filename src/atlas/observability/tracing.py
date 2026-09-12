"""LangSmith tracing configuration. Keys are never logged or returned by APIs."""

from __future__ import annotations

import os

from atlas.config.settings import Settings
from atlas.observability.logging import get_logger

logger = get_logger(__name__)


def configure_langsmith(settings: Settings) -> None:
    """Enable LangSmith only when explicitly configured."""
    if not settings.langsmith_tracing:
        os.environ.setdefault("LANGSMITH_TRACING", "false")
        return
    key = settings.langsmith_api_key
    if key is None or not key.get_secret_value():
        logger.warning("langsmith_enabled_without_key")
        os.environ["LANGSMITH_TRACING"] = "false"
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = key.get_secret_value()
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    logger.info("langsmith_configured", project=settings.langsmith_project)


def traceable_name(node: str) -> str:
    return f"atlas.{node}"
