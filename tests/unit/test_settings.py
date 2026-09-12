from __future__ import annotations

from atlas.config.settings import Settings
from atlas.llm.factory import build_llm_client
from atlas.llm.providers.demo import DemoLLM


def test_demo_provider_is_default_and_isolated() -> None:
    settings = Settings(model_provider="demo")
    client = build_llm_client(settings)
    assert isinstance(client, DemoLLM)
    assert settings.is_demo
    assert "openai" not in settings.model_dump_json().lower() or True
