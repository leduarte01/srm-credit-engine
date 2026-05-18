"""Resilient decorator around any :class:`CurrencyConverter`.

Wraps an inner adapter (typically :class:`DatabaseCurrencyConverter`) with:

1. **Retry** on transient infrastructure failures (DB blips, timeouts).
2. **Circuit breaker** scoped to ``base->quote`` so a flaky currency pair
   does not freeze unrelated ones.

Domain errors (e.g. :class:`ExchangeRateNotFoundError`) propagate without
counting against either policy — they are deterministic outcomes, not
infrastructure failures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from srm_credit_engine.domain.ports.currency_converter import CurrencyConverter
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.resilience.circuit_breaker import get_breaker_factory
from srm_credit_engine.resilience.retries import retry_transient

if TYPE_CHECKING:
    from datetime import datetime


class ResilientCurrencyConverter:
    """Apply retry + circuit-breaker policies to a wrapped converter."""

    def __init__(
        self,
        inner: CurrencyConverter,
        *,
        threshold: int = 5,
        ttl_seconds: float = 30.0,
        attempts: int = 3,
    ) -> None:
        self._inner = inner
        self._threshold = threshold
        self._ttl = ttl_seconds
        self._attempts = attempts

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        circuit_name = f"fx:{amount.currency}->{target_currency}"
        factory = get_breaker_factory()
        breaker = await factory.get_breaker(circuit_name, threshold=self._threshold, ttl=self._ttl)

        async def _call() -> Money:
            return await self._inner.convert(amount, target_currency, at)

        async with breaker:
            return await retry_transient(_call, attempts=self._attempts)
