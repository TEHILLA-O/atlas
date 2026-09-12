"""Embedding clients. Demo embeddings are deterministic and key-free."""

from __future__ import annotations

import hashlib
import math
from typing import Protocol

from atlas.config.settings import Settings


class EmbeddingClient(Protocol):
    dimensions: int

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class DemoEmbeddings:
    """Hash-projected embeddings that keep tests offline and deterministic."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [_hash_vector(text, self.dimensions) for text in texts]


class OpenAIEmbeddings:
    def __init__(self, settings: Settings) -> None:
        from langchain_openai import OpenAIEmbeddings as LCOpenAIEmbeddings

        key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        self.dimensions = settings.embedding_dimensions
        self._client = LCOpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=key,  # type: ignore[arg-type]
            dimensions=settings.embedding_dimensions,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)


class OllamaEmbeddings:
    def __init__(self, settings: Settings) -> None:
        from langchain_ollama import OllamaEmbeddings as LCOllamaEmbeddings

        self.dimensions = settings.embedding_dimensions
        self._client = LCOllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)


def build_embedding_client(settings: Settings) -> EmbeddingClient:
    if settings.embedding_provider == "openai":
        try:
            return OpenAIEmbeddings(settings)
        except Exception:
            return DemoEmbeddings(settings.embedding_dimensions)
    if settings.embedding_provider == "ollama":
        try:
            return OllamaEmbeddings(settings)
        except Exception:
            return DemoEmbeddings(settings.embedding_dimensions)
    return DemoEmbeddings(settings.embedding_dimensions)


def _hash_vector(text: str, dimensions: int) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    seed = digest
    while len(values) < dimensions:
        seed = hashlib.sha256(seed).digest()
        for byte in seed:
            values.append((byte / 127.5) - 1.0)
            if len(values) == dimensions:
                break
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]
