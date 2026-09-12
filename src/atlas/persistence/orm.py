"""SQLAlchemy ORM mappings for durable Atlas entities."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas.persistence.base import Base


def _uuid() -> str:
    return str(uuid4())


class ResearchSessionRow(Base):
    __tablename__ = "research_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="created")
    iteration: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    graph_thread_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list[ResearchTaskRow]] = relationship(back_populates="session")
    evidence: Mapped[list[EvidenceRow]] = relationship(back_populates="session")
    contradictions: Mapped[list[ContradictionRow]] = relationship(back_populates="session")
    reports: Mapped[list[ReportRow]] = relationship(back_populates="session")


class ResearchTaskRow(Base):
    __tablename__ = "research_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    purpose: Mapped[str] = mapped_column(Text)
    source_types: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped[ResearchSessionRow] = relationship(back_populates="tasks")


class EvidenceRow(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    claim: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    quote_or_excerpt: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(32))
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)
    source_quality: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    supports_claim: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ResearchSessionRow] = relationship(back_populates="evidence")


class ContradictionRow(Base):
    __tablename__ = "contradictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    topic: Mapped[str] = mapped_column(Text)
    claim_a: Mapped[str] = mapped_column(Text)
    claim_b: Mapped[str] = mapped_column(Text)
    evidence_a_id: Mapped[str] = mapped_column(String(36))
    evidence_b_id: Mapped[str] = mapped_column(String(36))
    severity: Mapped[str] = mapped_column(String(16), default="medium")
    possible_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    session: Mapped[ResearchSessionRow] = relationship(back_populates="contradictions")


class DocumentRow(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(128), default="upload")
    content_type: Mapped[str] = mapped_column(String(128))
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    byte_size: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks: Mapped[list[DocumentChunkRow]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunkRow(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(128), default="upload")
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(256), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    tsv: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped[DocumentRow] = relationship(back_populates="chunks")


class ReportRow(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(Text)
    markdown: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ResearchSessionRow] = relationship(back_populates="reports")


class FeedbackRow(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comments: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MemoryRow(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64), default="preference")
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UsageEventRow(Base):
    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    research_id: Mapped[str] = mapped_column(String(36), index=True)
    node: Mapped[str] = mapped_column(String(64))
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
