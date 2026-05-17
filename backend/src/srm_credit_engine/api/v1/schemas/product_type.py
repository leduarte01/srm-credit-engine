"""Schemas for the ProductType resource."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., description="Stable product code (e.g. DUPLICATA_MERCANTIL).")
    name: str
    monthly_spread: Decimal = Field(
        ..., description="Spread per month applied on top of base rate."
    )
    settlement_currency_code: str = Field(..., min_length=3, max_length=3)
