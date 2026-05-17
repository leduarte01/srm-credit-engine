"""Schemas for the pricing simulation endpoint (no persistence)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from srm_credit_engine.api.v1.schemas.common import MoneySchema


class PricingSimulateRequest(BaseModel):
    """Simulates the discount/settlement of a hypothetical receivable.

    No data is persisted — the endpoint is idempotent and pure.
    """

    product_code: str = Field(..., min_length=2, max_length=64)
    face_value: MoneySchema
    issue_date: date
    due_date: date
    reference_date: date | None = Field(
        default=None,
        description="Date used to compute remaining term. Defaults to issue_date.",
    )


class PricingSimulateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_code: str
    present_value: MoneySchema
    settlement_value: MoneySchema
    base_rate_monthly: Decimal
    spread_monthly: Decimal
    effective_monthly_rate: Decimal
    term_months: Decimal
    fx_rate_applied: Decimal | None
