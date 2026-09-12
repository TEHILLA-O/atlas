"""Local Ollama client."""

from __future__ import annotations

from langchain_ollama import ChatOllama
from pydantic import BaseModel

from atlas.config.settings import Settings
from atlas.llm.factory import extract_json_object
from atlas.llm.providers.openai_provider import _messages


class OllamaLLM:
    provider = "ollama"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.model_name
        self._client = ChatOllama(
            model=settings.model_name,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        result = await self._client.ainvoke(_messages(prompt, system))
        return str(result.content)

    async def structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
    ) -> BaseModel:
        text = await self.complete(
            f"{prompt}\nRespond with JSON matching {schema.model_json_schema()}",
            system=system,
        )
        return schema.model_validate(extract_json_object(text))
