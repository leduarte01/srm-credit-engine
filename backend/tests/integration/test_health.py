"""Smoke tests for app bootstrap and meta endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "srm-credit-engine"


@pytest.mark.asyncio
async def test_openapi_schema_is_served(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "SRM Credit Engine"
    assert "/v1/receivables" in spec["paths"]
    assert "/v1/settlements" in spec["paths"]
    assert "/v1/pricing/simulate" in spec["paths"]
