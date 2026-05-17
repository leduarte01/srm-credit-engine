"""Integration tests for the Exchange Rate endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_active_rate_seeded(client: AsyncClient) -> None:
    response = await client.get("/v1/fx-rates/USD/BRL")
    assert response.status_code == 200
    body = response.json()
    assert body["base_currency"] == "USD"
    assert body["quote_currency"] == "BRL"
    assert float(body["rate"]) > 0


@pytest.mark.asyncio
async def test_get_active_rate_unknown_pair_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/fx-rates/EUR/JPY")
    assert response.status_code == 404
    assert response.json()["code"] == "FX_RATE_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_fx_rate(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/fx-rates",
        json={
            "base_currency": "EUR",
            "quote_currency": "BRL",
            "rate": "6.20",
            "valid_from": "2024-06-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["base_currency"] == "EUR"
    assert body["valid_to"] is None


@pytest.mark.asyncio
async def test_create_fx_rate_rejects_same_currency(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/fx-rates",
        json={
            "base_currency": "BRL",
            "quote_currency": "BRL",
            "rate": "1.00",
            "valid_from": "2024-06-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_history(client: AsyncClient) -> None:
    response = await client.get("/v1/fx-rates/USD/BRL/history")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
