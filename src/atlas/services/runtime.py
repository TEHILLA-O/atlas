"""Compose tools, LLM, retriever and graph for a process."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from atlas.config.settings import Settings
from atlas.llm.embeddings import EmbeddingClient, build_embedding_client
from atlas.llm.factory import LLMClient, build_llm_client
from atlas.rag.retrieval import HybridRetriever, RetrievedChunk
from atlas.tools.calculator import CalculatorTool
from atlas.tools.database_search import DatabaseSearchTool, PreviousResearchTool
from atlas.tools.document_search import DocumentSearchTool, RetrieveChunksTool
from atlas.tools.registry import ToolRegistry, build_default_registry
from atlas.tools.web_fetch import WebFetchTool
from atlas.tools.web_search import WebSearchTool


async def _empty_lookup(_query: str) -> list[dict[str, object]]:
    return []


def build_tool_registry(
    settings: Settings,
    retrieve: Callable[..., Awaitable[list[RetrievedChunk]]] | None = None,
    lookup: Callable[[str], Awaitable[list[dict[str, object]]]] | None = None,
) -> ToolRegistry:
    async def _retrieve(query: str, **kwargs: object) -> list[RetrievedChunk]:
        if retrieve is None:
            return []
        return await retrieve(query, **kwargs)

    lookup_fn = lookup or _empty_lookup
    return build_default_registry(
        web_search=WebSearchTool(settings),
        web_fetch=WebFetchTool(settings),
        document_search=DocumentSearchTool(_retrieve),
        retrieve_chunks=RetrieveChunksTool(_retrieve),
        calculator=CalculatorTool(),
        database_search=DatabaseSearchTool(lookup_fn),
        previous_research=PreviousResearchTool(lookup_fn),
    )


class Runtime:
    """Process-wide collaborators. Domain logic stays outside FastAPI/Streamlit."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm: LLMClient = build_llm_client(settings)
        self.embeddings: EmbeddingClient = build_embedding_client(settings)
        self.retriever: HybridRetriever | None = None
        self.tools: ToolRegistry = build_tool_registry(settings)

    def bind_retriever(self, retriever: HybridRetriever) -> None:
        self.retriever = retriever

        async def _retrieve(query: str, **kwargs: object) -> list[RetrievedChunk]:
            document_ids = kwargs.get("document_ids")
            top_k = kwargs.get("top_k")
            return await retriever.retrieve(
                query,
                document_ids=document_ids if isinstance(document_ids, list) else None,
                top_k=top_k if isinstance(top_k, int) else None,
            )

        self.tools = build_tool_registry(self.settings, retrieve=_retrieve)
