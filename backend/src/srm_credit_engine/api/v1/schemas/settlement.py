"""Schemas for the Settlement resource and pricing simulation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from srm_credit_engine.api.v1.schemas.common import MoneySchema


class SettlementCreate(BaseModel):
    receivable_id: UUID
    reference_date: date | None = Field(
        default=None,
        description=(
            "Date used to compute remaining term. Defaults to the receivable's "
            "issue_date when omitted."
        ),
    )


class SettlementEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    occurred_at: datetime
    actor: str
    payload: dict[str, Any]


class SettlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    receivable_id: UUID
    discounted_value: MoneySchema
    settlement_currency: str
    settled_at: datetime
    base_rate_monthly: Decimal
    spread_monthly: Decimal
    term_months: Decimal
    fx_rate_applied: Decimal | None
    version: int
    events: list[SettlementEventResponse]
