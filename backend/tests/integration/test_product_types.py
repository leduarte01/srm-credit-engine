"""Integration tests for the ProductType endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_product_types(client: AsyncClient) -> None:
    response = await client.get("/v1/product-types")
    assert response.status_code == 200
    items = response.json()
    codes = {p["code"] for p in items}
    assert {"DUPLICATA_MERCANTIL", "CONTRATO_USD"}.issubset(codes)


@pytest.mark.asyncio
async def test_get_product_type_by_code(client: AsyncClient) -> None:
    response = await client.get("/v1/product-types/DUPLICATA_MERCANTIL")
    assert response.status_code == 200
    body = response.json()
    assert body["settlement_currency_code"] == "BRL"


@pytest.mark.asyncio
async def test_get_unknown_product_type_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/product-types/INEXISTENTE")
    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_TYPE_NOT_FOUND"
