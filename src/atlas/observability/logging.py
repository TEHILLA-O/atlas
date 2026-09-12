"""Structured JSON logging with request/correlation IDs. Secrets are never logged."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from atlas.config.settings import Settings

_SENSITIVE = {"api_key", "authorization", "password", "secret", "token"}


def _drop_secrets(
    _logger: Any, _method: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in event_dict.items():
        if any(token in key.lower() for token in _SENSITIVE):
            cleaned[key] = "***"
        else:
            cleaned[key] = value
    return cleaned


def configure_logging(settings: Settings) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        _drop_secrets,  # type: ignore[list-item]
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.env == "development" and settings.debug:
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)  # type: ignore[no-any-return]


def bind_request(*, request_id: str, correlation_id: str | None = None) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        correlation_id=correlation_id or request_id,
    )
