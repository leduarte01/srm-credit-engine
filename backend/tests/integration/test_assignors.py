"""Integration tests for the Assignor endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_assignor_succeeds(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/assignors",
        json={"document": "98765432000110", "legal_name": "Nova Cedente SA"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["document"] == "98765432000110"
    assert body["legal_name"] == "Nova Cedente SA"


@pytest.mark.asyncio
async def test_create_duplicate_assignor_returns_conflict(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/assignors",
        json={"document": "12345678000190", "legal_name": "Existing"},
    )
    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "CONCURRENCY_CONFLICT"


@pytest.mark.asyncio
async def test_get_by_document_returns_assignor(client: AsyncClient) -> None:
    response = await client.get("/v1/assignors/by-document/12345678000190")
    assert response.status_code == 200
    body = response.json()
    assert body["document"] == "12345678000190"


@pytest.mark.asyncio
async def test_get_by_document_unknown_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/assignors/by-document/00000000000000")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "ASSIGNOR_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_assignors_returns_pagination(client: AsyncClient) -> None:
    response = await client.get("/v1/assignors?limit=10")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["limit"] == 10
    assert body["meta"]["total"] >= 1
    assert any(a["document"] == "12345678000190" for a in body["items"])
