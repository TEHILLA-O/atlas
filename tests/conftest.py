"""Shared fixtures. Tests default to the demo provider and never need vendor keys."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("ATLAS_ENV", "test")
os.environ.setdefault("MODEL_PROVIDER", "demo")
os.environ.setdefault("EMBEDDING_PROVIDER", "demo")
os.environ.setdefault("ATLAS_HITL_ENABLED", "false")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from atlas.config.settings import Settings, reset_settings


@pytest.fixture
def settings() -> Settings:
    reset_settings()
    return Settings(env="test", model_provider="demo", embedding_provider="demo", hitl_enabled=False)
