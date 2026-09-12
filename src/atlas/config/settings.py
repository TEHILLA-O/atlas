"""Typed runtime configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderName = Literal["openai", "anthropic", "google", "ollama", "demo"]
EmbeddingProvider = Literal["openai", "ollama", "demo"]
RerankProvider = Literal["lexical", "cohere", "llm"]
EnvironmentName = Literal["development", "test", "staging", "production"]


class Settings(BaseSettings):
    """Central Atlas configuration. Domain code depends on this, not raw env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
        validate_by_name=True,
    )

    env: EnvironmentName = Field(default="development", alias="ATLAS_ENV")
    debug: bool = Field(default=False, alias="ATLAS_DEBUG")
    log_level: str = Field(default="INFO", alias="ATLAS_LOG_LEVEL")
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-to-a-long-random-string"),
        alias="ATLAS_SECRET_KEY",
    )
    api_host: str = Field(default="0.0.0.0", alias="ATLAS_API_HOST")
    api_port: int = Field(default=8000, alias="ATLAS_API_PORT")
    cors_origins: str = Field(
        default="http://localhost:8501,http://localhost:3000",
        alias="ATLAS_CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://atlas:atlas@localhost:5432/atlas",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg://atlas:atlas@localhost:5432/atlas",
        alias="DATABASE_URL_SYNC",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    model_provider: ProviderName = Field(default="demo", alias="MODEL_PROVIDER")
    model_name: str = Field(default="gpt-4.1-mini", alias="MODEL_NAME")
    embedding_provider: EmbeddingProvider = Field(
        default="demo", alias="EMBEDDING_PROVIDER"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small", alias="EMBEDDING_MODEL"
    )
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")

    openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: SecretStr | None = Field(default=None, alias="GOOGLE_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    rerank_provider: RerankProvider = Field(default="lexical", alias="RERANK_PROVIDER")
    cohere_api_key: SecretStr | None = Field(default=None, alias="COHERE_API_KEY")

    langsmith_tracing: bool = Field(default=False, alias="LANGSMITH_TRACING")
    langsmith_api_key: SecretStr | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="atlas", alias="LANGSMITH_PROJECT")
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT"
    )

    max_research_tasks: int = Field(default=8, alias="ATLAS_MAX_RESEARCH_TASKS")
    max_iterations: int = Field(default=2, alias="ATLAS_MAX_ITERATIONS")
    max_sources: int = Field(default=40, alias="ATLAS_MAX_SOURCES")
    max_tokens: int = Field(default=120_000, alias="ATLAS_MAX_TOKENS")
    research_budget_usd: float = Field(default=5.0, alias="ATLAS_RESEARCH_BUDGET_USD")
    max_parallel_tasks: int = Field(default=4, alias="ATLAS_MAX_PARALLEL_TASKS")

    top_k: int = Field(default=12, alias="ATLAS_TOP_K")
    rerank_k: int = Field(default=8, alias="ATLAS_RERANK_K")
    min_similarity: float = Field(default=0.15, alias="ATLAS_MIN_SIMILARITY")
    chunk_size: int = Field(default=800, alias="ATLAS_CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="ATLAS_CHUNK_OVERLAP")

    max_upload_mb: int = Field(default=20, alias="ATLAS_MAX_UPLOAD_MB")
    upload_dir: str = Field(default="./data/uploads", alias="ATLAS_UPLOAD_DIR")

    web_search_enabled: bool = Field(default=True, alias="ATLAS_WEB_SEARCH_ENABLED")
    allowed_url_schemes: str = Field(
        default="https,http", alias="ATLAS_ALLOWED_URL_SCHEMES"
    )
    blocked_hosts: str = Field(
        default="localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,169.254.169.254",
        alias="ATLAS_BLOCKED_HOSTS",
    )
    web_timeout_seconds: float = Field(default=15.0, alias="ATLAS_WEB_TIMEOUT_SECONDS")

    hitl_low_confidence: float = Field(default=0.7, alias="ATLAS_HITL_LOW_CONFIDENCE")
    hitl_high_impact: bool = Field(default=True, alias="ATLAS_HITL_HIGH_IMPACT")
    hitl_enabled: bool = Field(default=True, alias="ATLAS_HITL_ENABLED")
    enable_metrics: bool = Field(default=True, alias="ATLAS_ENABLE_METRICS")

    @field_validator("max_research_tasks", "max_iterations", "max_sources")
    @classmethod
    def _positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("budget limits must be >= 1")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def allowed_schemes(self) -> set[str]:
        return {item.strip() for item in self.allowed_url_schemes.split(",") if item.strip()}

    @property
    def blocked_host_list(self) -> list[str]:
        return [item.strip() for item in self.blocked_hosts.split(",") if item.strip()]

    @property
    def is_demo(self) -> bool:
        return self.model_provider == "demo"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()


def reset_settings() -> None:
    """Clear cached settings. Used by tests."""
    get_settings.cache_clear()
