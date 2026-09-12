"""Google Generative AI client."""

from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from atlas.config.settings import Settings
from atlas.llm.factory import extract_json_object
from atlas.llm.providers.openai_provider import _messages


class GoogleLLM:
    provider = "google"

    def __init__(self, settings: Settings) -> None:
        key = settings.google_api_key.get_secret_value() if settings.google_api_key else None
        self.model = settings.model_name
        self._client = ChatGoogleGenerativeAI(
            model=settings.model_name, google_api_key=key, temperature=0
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
        bound = self._client.with_structured_output(schema)
        try:
            result = await bound.ainvoke(_messages(prompt, system))
            if isinstance(result, schema):
                return result
            return schema.model_validate(result)
        except Exception:
            text = await self.complete(prompt, system=system)
            return schema.model_validate(extract_json_object(text))
