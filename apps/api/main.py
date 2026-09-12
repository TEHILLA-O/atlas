"""Thin shim matching the published repository layout."""

from atlas.apps.api.main import app, create_app, run

__all__ = ["app", "create_app", "run"]
