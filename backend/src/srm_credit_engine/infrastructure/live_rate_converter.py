"""Live FX rate adapter — fetches real-time quotes from fawazahmed0/exchange-api.

End-point used (CDN, no auth required, no rate limit):
  https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json

Fallback mirror (Cloudflare Pages):
  https://latest.currency-api.pages.dev/v1/currencies/{base}.json

Response shape:
  { "date": "2026-05-19", "{base}": { "{quote}": 0.1234, ... } }

Rates are cached in-process for ``_CACHE_TTL_SECONDS`` to avoid redundant
CDN requests when the simulator is called multiple times in quick succession.
"""

from __future__ import annotations

import time
from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.observability.metrics import FX_LOOKUPS

_PRIMARY_URL = (
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"
)
_FALLBACK_URL = "https://latest.currency-api.pages.dev/v1/currencies/{base}.json"
_TIMEOUT_SECONDS = 8.0
_CACHE_TTL_SECONDS = 60.0

# Module-level cache: { "BASE-QUOTE": (rate, fetched_at_monotonic) }
_rate_cache: dict[str, tuple[Decimal, float]] = {}


class LiveRateCurrencyConverter:
    """Fetches real-time FX rates from fawazahmed0/exchange-api (no auth, no rate limit).

    Uses jsDelivr CDN as primary and Cloudflare Pages as fallback mirror.
    Rates are cached in-process for 60 seconds.

    Raises :class:`ExchangeRateNotFoundError` when the pair is unsupported or
    both mirrors are unreachable, so callers can handle it uniformly.
    """

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:  # noqa: ARG002
        if amount.currency == target_currency:
            return amount

        rate = await self._fetch_rate(amount.currency, target_currency)
        FX_LOOKUPS.labels(amount.currency, target_currency, "live").inc()
        return Money(amount.amount * rate, target_currency).quantize(8)

    async def _fetch_rate(self, base: str, quote: str) -> Decimal:
        cache_key = f"{base.upper()}-{quote.upper()}"
        cached = _rate_cache.get(cache_key)
        if cached is not None:
            rate, fetched_at = cached
            if time.monotonic() - fetched_at < _CACHE_TTL_SECONDS:
                return rate

        base_lower = base.lower()
        quote_lower = quote.lower()

        data = await self._fetch_base_rates(base_lower)

        rates = data.get(base_lower)
        if rates is None or quote_lower not in rates:
            raise ExchangeRateNotFoundError(
                f"Pair {base.upper()}->{quote.upper()} not found in exchange-api response."
            )

        rate = Decimal(str(rates[quote_lower]))
        _rate_cache[cache_key] = (rate, time.monotonic())
        return rate

    async def _fetch_base_rates(self, base_lower: str) -> dict[str, Any]:
        """Fetch all rates for *base* currency, trying primary then fallback mirror."""
        last_exc: Exception | None = None

        for url_template in (_PRIMARY_URL, _FALLBACK_URL):
            url = url_template.format(base=base_lower)
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.json()  # type: ignore[no-any-return]
            except Exception as exc:
                last_exc = exc

        raise ExchangeRateNotFoundError(
            f"Live FX rate unavailable for base currency '{base_lower}': {last_exc}"
        ) from last_exc
