"""Integration tests for pricing simulation and settlement endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pricing_simulate_brl(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/pricing/simulate",
        json={
            "product_code": "DUPLICATA_MERCANTIL",
            "face_value": {"amount": "10000.00", "currency": "BRL"},
            "issue_date": "2024-01-10",
            "due_date": "2024-04-10",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["settlement_value"]["currency"] == "BRL"
    assert float(body["settlement_value"]["amount"]) < 10000  # discounted
    assert body["fx_rate_applied"] is None


@pytest.mark.asyncio
async def test_pricing_simulate_usd_settles_in_brl_with_fx(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/pricing/simulate",
        json={
            "product_code": "CONTRATO_USD",
            "face_value": {"amount": "1000.00", "currency": "USD"},
            "issue_date": "2024-01-10",
            "due_date": "2024-07-10",
        },
    )
    # CONTRATO_USD settles in USD per the seed — no FX expected.
    assert response.status_code == 200
    body = response.json()
    assert body["settlement_value"]["currency"] == "USD"


@pytest.mark.asyncio
async def test_pricing_simulate_unknown_product_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/pricing/simulate",
        json={
            "product_code": "INEXISTENTE",
            "face_value": {"amount": "1000.00", "currency": "BRL"},
            "issue_date": "2024-01-10",
            "due_date": "2024-04-10",
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_TYPE_NOT_FOUND"


@pytest.mark.asyncio
async def test_settle_full_flow(client: AsyncClient) -> None:
    create = await client.post(
        "/v1/receivables",
        json={
            "assignor_document": "12345678000190",
            "product_code": "DUPLICATA_MERCANTIL",
            "face_value": {"amount": "10000.00", "currency": "BRL"},
            "issue_date": "2024-01-10",
            "due_date": "2024-04-10",
            "external_reference": "NF-SETTLE",
        },
    )
    assert create.status_code == 201
    rid = create.json()["id"]

    settle = await client.post("/v1/settlements", json={"receivable_id": rid})
    assert settle.status_code == 201
    settlement = settle.json()
    assert settlement["receivable_id"] == rid
    event_types = {e["event_type"] for e in settlement["events"]}
    assert {"CREATED", "PRICED", "SETTLED"}.issubset(event_types)

    # Receivable status should now be SETTLED.
    final = await client.get(f"/v1/receivables/{rid}")
    assert final.json()["status"] == "SETTLED"


@pytest.mark.asyncio
async def test_settle_unknown_receivable_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/settlements",
        json={"receivable_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "RECEIVABLE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_settlement_unknown_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/settlements/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["code"] == "SETTLEMENT_NOT_FOUND"
