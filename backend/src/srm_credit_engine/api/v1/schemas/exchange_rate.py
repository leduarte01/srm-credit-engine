"""Schemas for the ExchangeRate resource."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExchangeRateCreate(BaseModel):
    base_currency: str = Field(..., min_length=3, max_length=3)
    quote_currency: str = Field(..., min_length=3, max_length=3)
    rate: Decimal = Field(..., gt=0)
    valid_from: datetime
    valid_to: datetime | None = None

    @model_validator(mode="after")
    def _check(self) -> ExchangeRateCreate:
        if self.base_currency.upper() == self.quote_currency.upper():
            raise ValueError("base_currency and quote_currency must differ.")
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be strictly greater than valid_from.")
        return self


class ExchangeRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    base_currency: str
    quote_currency: str
    rate: Decimal
    valid_from: datetime
    valid_to: datetime | None
