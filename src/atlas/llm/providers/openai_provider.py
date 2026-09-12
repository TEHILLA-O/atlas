"""OpenAI-backed LLM client."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from atlas.config.settings import Settings
from atlas.llm.factory import extract_json_object


class OpenAILLM:
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        self.model = settings.model_name
        self._client = ChatOpenAI(
            model=settings.model_name,
            api_key=key,  # type: ignore[arg-type]
            temperature=0,
        )

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = _messages(prompt, system)
        result = await self._client.ainvoke(messages)
        return str(result.content)

    async def structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
    ) -> BaseModel:
        bound = self._client.with_structured_output(schema)
        try:
            result = await bound.ainvoke(_messages(prompt, system))
            if isinstance(result, schema):
                return result
            return schema.model_validate(result)
        except Exception:
            text = await self.complete(prompt, system=system)
            return schema.model_validate(extract_json_object(text))


def _messages(prompt: str, system: str | None) -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))
    return messages
