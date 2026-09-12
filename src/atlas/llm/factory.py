"""LLM factory. Domain code talks only to LLMClient, never a vendor SDK."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel

from atlas.config.settings import Settings
from atlas.llm.providers.demo import DemoLLM
from atlas.observability.logging import get_logger

logger = get_logger(__name__)


class LLMClient(Protocol):
    """Minimal structured-generation contract used by agents."""

    provider: str
    model: str

    async def complete(self, prompt: str, *, system: str | None = None) -> str: ...

    async def structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
    ) -> BaseModel: ...


def build_llm_client(settings: Settings) -> LLMClient:
    provider = settings.model_provider
    if provider == "demo":
        return DemoLLM(model=settings.model_name)
    try:
        if provider == "openai":
            from atlas.llm.providers.openai_provider import OpenAILLM

            return OpenAILLM(settings)
        if provider == "anthropic":
            from atlas.llm.providers.anthropic_provider import AnthropicLLM

            return AnthropicLLM(settings)
        if provider == "google":
            from atlas.llm.providers.google_provider import GoogleLLM

            return GoogleLLM(settings)
        if provider == "ollama":
            from atlas.llm.providers.ollama_provider import OllamaLLM

            return OllamaLLM(settings)
    except Exception as exc:  # pragma: no cover - import/runtime fallback
        logger.warning("llm_provider_fallback_demo", provider=provider, error=str(exc))
        return DemoLLM(model=settings.model_name)
    raise ValueError(f"unsupported model provider: {provider}")


def usage_estimate(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """Rough USD estimate used for budget control, not billing."""
    rates: dict[str, tuple[float, float]] = {
        "gpt-4.1-mini": (0.40, 1.60),
        "gpt-4o": (2.50, 10.00),
        "claude-3-5-sonnet": (3.00, 15.00),
        "gemini-2.0-flash": (0.10, 0.40),
    }
    inp, out = rates.get(model, (1.00, 5.00))
    return (prompt_tokens * inp + completion_tokens * out) / 1_000_000


def extract_json_object(text: str) -> dict[str, Any]:
    """Best-effort JSON object extraction from a model response."""
    import json
    import re

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("no JSON object in model output")
    parsed: dict[str, Any] = json.loads(match.group(0))
    return parsed
