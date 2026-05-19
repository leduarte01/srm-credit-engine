"""Fallback currency converter — tries primary, then secondary on miss.

Typical wiring:
    FallbackCurrencyConverter(
        primary=DatabaseCurrencyConverter(rates),
        secondary=LiveRateCurrencyConverter(),
    )

The ``last_source`` attribute is set after every successful conversion and
can be inspected by the caller (safe because FastAPI creates a new instance
per request via Depends).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.ports.currency_converter import CurrencyConverter
from srm_credit_engine.domain.value_objects.money import Money


class FallbackCurrencyConverter:
    """Try *primary*; on :class:`ExchangeRateNotFoundError`, try *secondary*."""

    def __init__(self, primary: CurrencyConverter, secondary: CurrencyConverter) -> None:
        self._primary = primary
        self._secondary = secondary
        self.last_source: Literal["database", "live"] | None = None

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        if amount.currency == target_currency:
            self.last_source = None
            return amount

        try:
            result = await self._primary.convert(amount, target_currency, at)
            self.last_source = "database"
            return result
        except ExchangeRateNotFoundError:
            result = await self._secondary.convert(amount, target_currency, at)
            self.last_source = "live"
            return result
