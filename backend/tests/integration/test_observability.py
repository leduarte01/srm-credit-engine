"""Integration tests for observability surface: ``/metrics`` and request id."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_request_id_header(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in {k.lower() for k in response.headers}


@pytest.mark.asyncio
async def test_health_echoes_incoming_request_id(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "trace-abc-123"})
    assert response.headers.get("x-request-id") == "trace-abc-123"


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_text(client: AsyncClient) -> None:
    # Hit a route first so at least one counter is populated.
    await client.get("/health")
    response = await client.get("/metrics")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("text/plain")
    body = response.text
    assert "srm_http_requests_total" in body
    assert "srm_http_request_duration_seconds" in body


@pytest.mark.asyncio
async def test_metrics_counter_increments_on_request(client: AsyncClient) -> None:
    await client.get("/health")
    before = await client.get("/metrics")
    await client.get("/health")
    await client.get("/health")
    after = await client.get("/metrics")
    # The Prometheus text format embeds counters as floating point literals.
    # A naive substring check would be brittle; instead, parse the count for
    # the /health 200 series and assert it strictly increased by 2.
    before_count = _extract_health_counter(before.text)
    after_count = _extract_health_counter(after.text)
    assert after_count == before_count + 2


def _extract_health_counter(payload: str) -> float:
    target = 'srm_http_requests_total{method="GET",route="/health",status="200"}'
    for line in payload.splitlines():
        if line.startswith(target):
            return float(line.split()[-1])
    return 0.0
