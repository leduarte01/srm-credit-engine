"""Prometheus metrics — counters, histograms and the ``/metrics`` payload."""

from __future__ import annotations

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

REGISTRY = CollectorRegistry(auto_describe=True)

HTTP_REQUESTS_TOTAL = Counter(
    "srm_http_requests_total",
    "Total HTTP requests handled by the API, partitioned by method, route and status.",
    labelnames=("method", "route", "status"),
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "srm_http_request_duration_seconds",
    "Latency of HTTP requests in seconds.",
    labelnames=("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)

PRICING_OPERATIONS = Counter(
    "srm_pricing_operations_total",
    "Pricing operations executed, partitioned by product code and outcome.",
    labelnames=("product_code", "outcome"),
    registry=REGISTRY,
)

SETTLEMENT_OPERATIONS = Counter(
    "srm_settlement_operations_total",
    "Settlement operations executed, partitioned by product code and outcome.",
    labelnames=("product_code", "outcome"),
    registry=REGISTRY,
)

FX_LOOKUPS = Counter(
    "srm_fx_lookups_total",
    "FX rate lookups performed, partitioned by base/quote currency and outcome.",
    labelnames=("base", "quote", "outcome"),
    registry=REGISTRY,
)


def metrics_response() -> Response:
    """Return the current Prometheus text exposition payload."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
