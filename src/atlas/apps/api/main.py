"""FastAPI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from atlas import __version__
from atlas.apps.api.errors import register_exception_handlers
from atlas.apps.api.routers import documents, feedback, health, research
from atlas.config.settings import Settings, get_settings
from atlas.observability.logging import bind_request, configure_logging, get_logger
from atlas.observability.tracing import configure_langsmith
from atlas.persistence.base import Base
from atlas.persistence.session import get_engine
from atlas.services.runtime import Runtime

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    configure_langsmith(settings)
    app.state.settings = settings
    app.state.runtime = Runtime(settings)
    if settings.env in {"development", "test"}:
        try:
            await _create_schema(settings)
        except Exception as exc:
            logger.warning("schema_bootstrap_skipped", error=str(exc))
    logger.info("atlas_api_started", version=__version__, env=settings.env)
    yield
    logger.info("atlas_api_stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    application = FastAPI(
        title="Atlas",
        description=(
            "Agentic research, knowledge retrieval and decision intelligence. "
            "Not a chatbot: Atlas plans research, retrieves evidence, detects "
            "contradictions and produces cited reports."
        ),
        version=__version__,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(application)
    application.include_router(health.router)
    application.include_router(research.router)
    application.include_router(documents.router)
    application.include_router(feedback.router)

    @application.middleware("http")
    async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("x-request-id", str(uuid4()))
        correlation_id = request.headers.get("x-correlation-id", request_id)
        bind_request(request_id=request_id, correlation_id=correlation_id)
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers["x-correlation-id"] = correlation_id
        return response

    @application.get("/")
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "name": "Atlas",
                "version": __version__,
                "docs": "/docs",
                "health": "/health",
            }
        )

    return application


async def _create_schema(settings: Settings) -> None:
    engine = get_engine(settings)
    async with engine.begin() as conn:
        await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.run_sync(Base.metadata.create_all)


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "atlas.apps.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
