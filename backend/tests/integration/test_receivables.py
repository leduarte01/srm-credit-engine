"""Integration tests for the Receivables endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


def _payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "assignor_document": "12345678000190",
        "product_code": "DUPLICATA_MERCANTIL",
        "face_value": {"amount": "10000.00", "currency": "BRL"},
        "issue_date": "2024-01-10",
        "due_date": "2024-04-10",
        "external_reference": "NF-001",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_create_and_get_receivable(client: AsyncClient) -> None:
    create = await client.post("/v1/receivables", json=_payload())
    assert create.status_code == 201
    created = create.json()
    rid = created["id"]
    assert created["status"] == "PENDING"

    fetched = await client.get(f"/v1/receivables/{rid}")
    assert fetched.status_code == 200
    assert fetched.json()["external_reference"] == "NF-001"


@pytest.mark.asyncio
async def test_create_receivable_unknown_assignor_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/receivables", json=_payload(assignor_document="00000000000000")
    )
    assert response.status_code == 404
    assert response.json()["code"] == "ASSIGNOR_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_receivable_validates_dates(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/receivables",
        json=_payload(issue_date="2024-04-10", due_date="2024-01-10"),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_with_filters(client: AsyncClient) -> None:
    await client.post("/v1/receivables", json=_payload(external_reference="NF-A"))
    await client.post(
        "/v1/receivables",
        json=_payload(
            external_reference="NF-B",
            product_code="CONTRATO_USD",
            face_value={"amount": "5000.00", "currency": "USD"},
        ),
    )

    response = await client.get("/v1/receivables?product_code=CONTRATO_USD")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 1
    assert all(r["product_code"] == "CONTRATO_USD" for r in body["items"])


@pytest.mark.asyncio
async def test_cancel_receivable(client: AsyncClient) -> None:
    create = await client.post("/v1/receivables", json=_payload(external_reference="NF-CANCEL"))
    rid = create.json()["id"]
    response = await client.patch(f"/v1/receivables/{rid}/cancel")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_get_receivable_unknown_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/receivables/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["code"] == "RECEIVABLE_NOT_FOUND"
