"""Private-document analyst. Tools: search_documents, retrieve_document_chunks."""

from __future__ import annotations

from atlas.llm.factory import LLMClient
from atlas.models.enums import SourceQuality, SourceType
from atlas.models.evidence import Evidence
from atlas.models.research import ResearchResult, ResearchTask
from atlas.prompts.templates import DOCUMENT_ANALYST_SYSTEM
from atlas.rag.source_quality import classify_source, reliability_for
from atlas.security.injection import isolate_untrusted_text
from atlas.tools.registry import ToolRegistry


class DocumentAnalystAgent:
    allowed_tools = ("search_documents", "retrieve_document_chunks")

    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools.restrict(self.allowed_tools)

    async def run(self, task: ResearchTask) -> tuple[ResearchResult, list[Evidence]]:
        result = await self.tools.invoke("search_documents", {"query": task.question})
        evidence: list[Evidence] = []
        findings: list[str] = []
        errors: list[str] = []
        if not result.ok:
            errors.append(result.error.message if result.error else "document search failed")
        for row in result.data.get("results", []):
            content = str(row.get("content", ""))
            isolate_untrusted_text(content, source=str(row.get("filename", "document")))
            quality = classify_source(
                filename=str(row.get("filename", "")), source_hint="company"
            )
            evidence.append(
                Evidence(
                    claim=task.question,
                    document_id=str(row.get("document_id")),
                    quote_or_excerpt=content[:1200],
                    source_type=SourceType.DOCUMENT,
                    relevance_score=float(row.get("score", 0.5)),
                    reliability_score=reliability_for(quality),
                    source_quality=quality if quality != SourceQuality.UNKNOWN else SourceQuality.COMPANY_SOURCE,
                    supports_claim=True,
                    metadata={
                        "filename": row.get("filename"),
                        "page": row.get("page"),
                        "section": row.get("section"),
                    },
                )
            )
            findings.append(content[:240])
        _ = DOCUMENT_ANALYST_SYSTEM
        return (
            ResearchResult(
                task_id=task.id,
                summary=findings[0] if findings else "No matching private documents.",
                findings=findings[:8],
                evidence_ids=[item.evidence_id for item in evidence],
                sources_consulted=len(evidence),
                errors=errors,
                completed=True,
            ),
            evidence,
        )
