"""Report projections: Markdown and JSON. PDF is intentionally omitted."""

from __future__ import annotations

from atlas.models.report import ResearchReport


def render_markdown(report: ResearchReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        "## Executive Summary",
        report.executive_summary,
        "",
        "## Research Question",
        report.research_question,
        "",
        "## Recommendation",
        report.recommendation,
        "",
        "## Key Findings",
        *_bullets(report.key_findings),
        "",
        "## Opportunities",
        *_bullets(report.opportunities),
        "",
        "## Risks",
        *_bullets(report.risks),
        "",
        "## Evidence",
    ]
    if not report.evidence:
        lines.append("- None recorded.")
    for evidence in report.evidence:
        source = evidence.source_url or evidence.document_id or "internal"
        lines.append(
            f"- `{evidence.evidence_id}` ({evidence.source_quality.value}, {source}): "
            f"{evidence.quote_or_excerpt}"
        )
    lines.extend(["", "## Contradictory Evidence"])
    if not report.contradictions:
        lines.append("- None detected.")
    for contradiction in report.contradictions:
        status = "resolved" if contradiction.resolved else "unresolved"
        lines.append(
            f"- **{contradiction.topic}** ({contradiction.severity.value}, {status}): "
            f"{contradiction.claim_a} vs {contradiction.claim_b}. "
            f"{contradiction.possible_explanation or ''}"
        )
    lines.extend(
        [
            "",
            "## Unknowns / Data Gaps",
            *_bullets(report.unknowns),
            "",
            "## Confidence Assessment",
            f"- Overall: {report.confidence.as_percent()}% "
            f"(decision-support score, not a calibrated probability)",
            f"- Evidence quality: {report.confidence.evidence_quality}",
            f"- Source agreement: {report.confidence.source_agreement}",
            f"- Coverage: {report.confidence.coverage}",
            f"- {report.confidence.rationale}",
            "",
            "## Critic Notes",
            *_bullets(report.critic_notes),
            "",
            "## Sources",
            *_bullets(report.sources, empty="- No sources recorded."),
            "",
            "## Citations",
        ]
    )
    if not report.citations:
        lines.append("- None recorded.")
    for citation in report.citations:
        verified = "verified" if citation.verified else "unverified"
        lines.append(
            f"- Claim `{citation.claim_id}` → evidence `{citation.evidence_id}` "
            f"({verified}) {citation.source_ref}"
        )
    unsupported = [claim.statement for claim in report.claims if not claim.supported]
    if unsupported:
        lines.extend(["", "## Unsupported Claims", *_bullets(unsupported)])
    return "\n".join(lines)


def _bullets(items: list[str], empty: str = "- None recorded.") -> list[str]:
    return [f"- {item}" for item in items] if items else [empty]
