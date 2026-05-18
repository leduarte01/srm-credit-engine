"""Observability package: structured logging, tracing and metrics."""

from __future__ import annotations

from srm_credit_engine.observability.logging import configure_logging, get_logger
from srm_credit_engine.observability.metrics import (
    FX_LOOKUPS,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    PRICING_OPERATIONS,
    SETTLEMENT_OPERATIONS,
    metrics_response,
)
from srm_credit_engine.observability.tracing import configure_tracing

__all__ = [
    "FX_LOOKUPS",
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "PRICING_OPERATIONS",
    "SETTLEMENT_OPERATIONS",
    "configure_logging",
    "configure_tracing",
    "get_logger",
    "metrics_response",
]
