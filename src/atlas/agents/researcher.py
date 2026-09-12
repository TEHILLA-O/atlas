"""Public-source researcher. Tools: web_search, fetch_web_page, calculator."""

from __future__ import annotations

from atlas.llm.factory import LLMClient
from atlas.models.enums import SourceType
from atlas.models.evidence import Evidence
from atlas.models.research import ResearchResult, ResearchTask
from atlas.prompts.templates import RESEARCHER_SYSTEM
from atlas.rag.source_quality import classify_source, reliability_for
from atlas.security.injection import isolate_untrusted_text
from atlas.tools.registry import ToolRegistry


class ResearcherAgent:
    allowed_tools = ("web_search", "fetch_web_page", "calculator")

    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools.restrict(self.allowed_tools)

    async def run(self, task: ResearchTask, queries: list[str]) -> tuple[ResearchResult, list[Evidence]]:
        evidence: list[Evidence] = []
        errors: list[str] = []
        findings: list[str] = []
        for query in queries:
            result = await self.tools.invoke("web_search", {"query": query, "max_results": 5})
            if not result.ok:
                errors.append(result.error.message if result.error else "web_search failed")
                continue
            rows = result.data.get("results", [])
            for row in rows:
                snippet = str(row.get("snippet", ""))
                url = str(row.get("url", ""))
                isolate_untrusted_text(snippet, source=url)
                quality = classify_source(url=url)
                evidence.append(
                    Evidence(
                        claim=task.question,
                        source_url=url,
                        quote_or_excerpt=snippet,
                        source_type=SourceType.WEB,
                        relevance_score=min(1.0, 0.4 + 0.1 * int(row.get("overlap", 1))),
                        reliability_score=float(row.get("reliability", reliability_for(quality))),
                        source_quality=quality,
                        supports_claim=True,
                        metadata={"title": row.get("title"), "query": query},
                    )
                )
                findings.append(snippet)
        _ = RESEARCHER_SYSTEM
        return (
            ResearchResult(
                task_id=task.id,
                summary=findings[0] if findings else "No public sources returned.",
                findings=findings[:8],
                evidence_ids=[item.evidence_id for item in evidence],
                sources_consulted=len(evidence),
                errors=errors,
                completed=not errors or bool(evidence),
            ),
            evidence,
        )
