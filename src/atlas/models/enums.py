"""Shared enumerations. Kept independent of persistence and LLM providers."""

from __future__ import annotations

from enum import StrEnum


class IntentType(StrEnum):
    MARKET_ANALYSIS = "market_analysis"
    OPPORTUNITY_ASSESSMENT = "opportunity_assessment"
    SUPPLIER_COMPARISON = "supplier_comparison"
    DUE_DILIGENCE = "due_diligence"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    GENERAL_RESEARCH = "general_research"


class ResearchStatus(StrEnum):
    CREATED = "created"
    CLASSIFYING = "classifying"
    PLANNING = "planning"
    RESEARCHING = "researching"
    RETRIEVING = "retrieving"
    ANALYSING = "analysing"
    VERIFYING = "verifying"
    AWAITING_HUMAN = "awaiting_human"
    SYNTHESISING = "synthesising"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SourceType(StrEnum):
    WEB = "web"
    DOCUMENT = "document"
    DATABASE = "database"
    MEMORY = "memory"
    CALCULATOR = "calculator"
    USER = "user"


class SourceQuality(StrEnum):
    PRIMARY = "PRIMARY"
    GOVERNMENT = "GOVERNMENT"
    ACADEMIC = "ACADEMIC"
    COMPANY_SOURCE = "COMPANY_SOURCE"
    ESTABLISHED_MEDIA = "ESTABLISHED_MEDIA"
    INDUSTRY = "INDUSTRY"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"


class TaskPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HumanDecision(StrEnum):
    APPROVE = "approve"
    REQUEST_MORE_RESEARCH = "request_more_research"
    CANCEL = "cancel"


class ContradictionSeverity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
