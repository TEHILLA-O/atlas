"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-09-12
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "research_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("iteration", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("graph_thread_id", sa.String(64)),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "research_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), sa.ForeignKey("research_sessions.id")),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("source_types", JSONB(), nullable=False, server_default="[]"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("result_summary", sa.Text()),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), sa.ForeignKey("research_sessions.id")),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text()),
        sa.Column("document_id", sa.String(36)),
        sa.Column("quote_or_excerpt", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("reliability_score", sa.Float(), nullable=False),
        sa.Column("source_quality", sa.String(32), nullable=False),
        sa.Column("supports_claim", sa.Boolean(), nullable=False),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "contradictions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), sa.ForeignKey("research_sessions.id")),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("claim_a", sa.Text(), nullable=False),
        sa.Column("claim_b", sa.Text(), nullable=False),
        sa.Column("evidence_a_id", sa.String(36), nullable=False),
        sa.Column("evidence_b_id", sa.String(36), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("possible_explanation", sa.Text()),
        sa.Column("resolved", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id")),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("page", sa.Integer()),
        sa.Column("section", sa.String(256)),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tsv", sa.Text()),
        sa.Column("embedding", Vector(1536)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), sa.ForeignKey("research_sessions.id")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), sa.ForeignKey("research_sessions.id")),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=False),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "memories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("key", sa.String(256), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "usage_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_id", sa.String(36), nullable=False),
        sa.Column("node", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128)),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_evidence_research_id", "evidence", ["research_id"])


def downgrade() -> None:
    op.drop_table("usage_events")
    op.drop_table("memories")
    op.drop_table("feedback")
    op.drop_table("reports")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("contradictions")
    op.drop_table("evidence")
    op.drop_table("research_tasks")
    op.drop_table("research_sessions")
