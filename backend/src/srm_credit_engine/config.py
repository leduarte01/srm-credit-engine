"""Application settings loaded from environment variables (12-factor)."""

from __future__ import annotations

from decimal import Decimal
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration. Immutable across the process lifetime."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="local")
    app_name: str = Field(default="srm-credit-engine")
    app_version: str = Field(default="1.0.0")
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True)

    # API
    api_host: str = Field(default="0.0.0.0")  # noqa: S104 — bind explícito para container
    api_port: int = Field(default=8000)
    api_cors_origins: str = Field(default="http://localhost:5173")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://srm:srm@localhost:5432/srm_credit"
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=5)
    database_echo: bool = Field(default=False)

    # Observability
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str = Field(default="srm-credit-engine")
    prometheus_enabled: bool = Field(default=True)

    # Pricing
    base_rate_monthly: Decimal = Field(default=Decimal("0.01"))

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor — single source of truth across the app."""
    return Settings()
