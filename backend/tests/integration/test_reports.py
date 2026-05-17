"""Integration tests for the analytical /v1/reports endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_receivable(
    client: AsyncClient,
    *,
    product_code: str,
    amount: str,
    currency: str,
    external_reference: str,
    issue_date: str = "2024-01-10",
    due_date: str = "2024-04-10",
) -> str:
    response = await client.post(
        "/v1/receivables",
        json={
            "assignor_document": "12345678000190",
            "product_code": product_code,
            "face_value": {"amount": amount, "currency": currency},
            "issue_date": issue_date,
            "due_date": due_date,
            "external_reference": external_reference,
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


async def _settle(client: AsyncClient, receivable_id: str) -> dict[str, object]:
    response = await client.post("/v1/settlements", json={"receivable_id": receivable_id})
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_volume_by_assignor_aggregates_settled_receivables(client: AsyncClient) -> None:
    r1 = await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="10000.00",
        currency="BRL",
        external_reference="NF-VOL-1",
    )
    r2 = await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="5000.00",
        currency="BRL",
        external_reference="NF-VOL-2",
    )
    await _settle(client, r1)
    await _settle(client, r2)

    response = await client.get(
        "/v1/reports/volume-by-assignor",
        params={
            "period_start": "2000-01-01T00:00:00+00:00",
            "period_end": "2100-01-01T00:00:00+00:00",
            "limit": 5,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["assignor_document"] == "12345678000190"
    assert row["receivable_count"] == 2
    assert float(row["total_face_value"]) == pytest.approx(15000.0)
    assert float(row["total_present_value"]) > 0


@pytest.mark.asyncio
async def test_volume_by_assignor_empty_period_returns_no_rows(client: AsyncClient) -> None:
    response = await client.get(
        "/v1/reports/volume-by-assignor",
        params={
            "period_start": "1990-01-01T00:00:00+00:00",
            "period_end": "1990-02-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 200
    assert response.json()["rows"] == []


@pytest.mark.asyncio
async def test_pnl_by_product_computes_revenue(client: AsyncClient) -> None:
    rid = await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="10000.00",
        currency="BRL",
        external_reference="NF-PNL-1",
    )
    await _settle(client, rid)

    response = await client.get(
        "/v1/reports/pnl-by-product",
        params={
            "period_start": "2000-01-01T00:00:00+00:00",
            "period_end": "2100-01-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 200
    rows = response.json()["rows"]
    assert len(rows) == 1
    row = rows[0]
    assert row["product_code"] == "DUPLICATA_MERCANTIL"
    assert row["settlement_currency"] == "BRL"
    assert float(row["total_revenue"]) > 0
    # Revenue is exactly face_value - advanced
    assert float(row["total_revenue"]) == pytest.approx(
        float(row["total_face_value_in_settlement_currency"]) - float(row["total_advanced"])
    )


@pytest.mark.asyncio
async def test_aging_buckets_classifies_pending_receivables(client: AsyncClient) -> None:
    # Create three receivables with different due dates relative to a fixed reference.
    await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="1000.00",
        currency="BRL",
        external_reference="NF-AGE-OVERDUE",
        issue_date="2023-01-01",
        due_date="2023-12-01",
    )
    await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="2000.00",
        currency="BRL",
        external_reference="NF-AGE-30",
        issue_date="2024-01-01",
        due_date="2024-01-20",
    )
    await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="3000.00",
        currency="BRL",
        external_reference="NF-AGE-FAR",
        issue_date="2024-01-01",
        due_date="2024-12-31",
    )

    response = await client.get(
        "/v1/reports/aging-buckets",
        params={"reference_date": "2024-01-01T00:00:00+00:00"},
    )
    assert response.status_code == 200
    buckets = {row["bucket"]: row for row in response.json()["rows"]}
    assert buckets["OVERDUE"]["receivable_count"] == 1
    assert buckets["0_30"]["receivable_count"] == 1
    assert buckets["90_PLUS"]["receivable_count"] == 1


@pytest.mark.asyncio
async def test_aging_buckets_excludes_settled(client: AsyncClient) -> None:
    rid = await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="1000.00",
        currency="BRL",
        external_reference="NF-AGE-SETTLED",
    )
    await _settle(client, rid)

    response = await client.get(
        "/v1/reports/aging-buckets",
        params={"reference_date": "2024-05-01T00:00:00+00:00"},
    )
    assert response.status_code == 200
    assert response.json()["rows"] == []


@pytest.mark.asyncio
async def test_fx_exposure_groups_by_currency(client: AsyncClient) -> None:
    await _create_receivable(
        client,
        product_code="DUPLICATA_MERCANTIL",
        amount="10000.00",
        currency="BRL",
        external_reference="NF-FX-BRL",
    )
    await _create_receivable(
        client,
        product_code="CONTRATO_USD",
        amount="2000.00",
        currency="USD",
        external_reference="NF-FX-USD",
    )

    response = await client.get("/v1/reports/fx-exposure")
    assert response.status_code == 200
    rows = {row["currency"]: row for row in response.json()["rows"]}
    assert float(rows["BRL"]["total_face_value"]) == pytest.approx(10000.0)
    assert float(rows["USD"]["total_face_value"]) == pytest.approx(2000.0)


@pytest.mark.asyncio
async def test_volume_by_assignor_rejects_invalid_period(client: AsyncClient) -> None:
    response = await client.get(
        "/v1/reports/volume-by-assignor",
        params={
            "period_start": "2024-12-01T00:00:00+00:00",
            "period_end": "2024-01-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
