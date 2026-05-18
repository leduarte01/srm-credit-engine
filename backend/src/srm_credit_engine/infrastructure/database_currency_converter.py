"""Currency conversion adapter backed by the ``exchange_rate`` repository."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.ports.repositories import ExchangeRateRepository
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.observability.metrics import FX_LOOKUPS


class DatabaseCurrencyConverter:
    """Converts money amounts using the persisted FX rates.

    Strategy:

    1. Try a direct ``base -> target`` active rate.
    2. Fallback to the inverse ``target -> base`` rate (``1 / rate``).
    3. If neither exists, raise :class:`ExchangeRateNotFoundError`.

    Cross-currency triangulation (e.g. via USD) is intentionally left out of
    this MVP — the seed only carries direct USD<->BRL pairs.
    """

    def __init__(self, rates: ExchangeRateRepository) -> None:
        self._rates = rates

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        if amount.currency == target_currency:
            return amount

        direct = await self._rates.get_active(amount.currency, target_currency, at)
        if direct is not None:
            FX_LOOKUPS.labels(amount.currency, target_currency, "direct").inc()
            return Money(amount.amount * direct.rate, target_currency).quantize(8)

        inverse = await self._rates.get_active(target_currency, amount.currency, at)
        if inverse is not None:
            FX_LOOKUPS.labels(amount.currency, target_currency, "inverse").inc()
            inverted_rate = Decimal("1") / inverse.rate
            return Money(amount.amount * inverted_rate, target_currency).quantize(8)

        FX_LOOKUPS.labels(amount.currency, target_currency, "missing").inc()
        raise ExchangeRateNotFoundError(
            f"No FX rate available between {amount.currency} and {target_currency} at {at!s}."
        )
