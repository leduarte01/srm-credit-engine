"""Live FX rate adapter — fetches real-time quotes from AwesomeAPI (BR).

End-point used: https://economia.awesomeapi.com.br/json/last/{BASE}-{QUOTE}
No authentication required. Free tier, no rate limit for low volume.

Rates are cached in-process for ``_CACHE_TTL_SECONDS`` to avoid hitting the
free-tier rate limit (HTTP 429) on repeated simulator calls.
"""

from __future__ import annotations

import time
from datetime import datetime
from decimal import Decimal

import httpx

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.observability.metrics import FX_LOOKUPS

_AWESOMEAPI_URL = "https://economia.awesomeapi.com.br/json/last/{base}-{quote}"
_TIMEOUT_SECONDS = 5.0
_CACHE_TTL_SECONDS = 60.0

# Module-level cache: { "BASE-QUOTE": (rate, fetched_at_monotonic) }
_rate_cache: dict[str, tuple[Decimal, float]] = {}


class LiveRateCurrencyConverter:
    """Fetches real-time FX rates from AwesomeAPI with a 60-second in-process cache.

    The cache prevents HTTP 429 (Too Many Requests) errors on the free tier
    when the simulator is called in quick succession.

    Raises :class:`ExchangeRateNotFoundError` when the pair is unsupported or
    the external API is unreachable, so callers can handle it uniformly.
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

        url = _AWESOMEAPI_URL.format(base=base.upper(), quote=quote.upper())
        pair_key = f"{base.upper()}{quote.upper()}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            # Try inverse pair
            try:
                return await self._fetch_rate_inverse(base, quote)
            except Exception:
                raise ExchangeRateNotFoundError(
                    f"Live FX rate unavailable for {base}->{quote}: {exc}"
                ) from exc

        if pair_key not in data:
            try:
                return await self._fetch_rate_inverse(base, quote)
            except Exception:
                raise ExchangeRateNotFoundError(
                    f"Pair {base}->{quote} not found in AwesomeAPI response."
                ) from None

        bid = data[pair_key].get("bid") or data[pair_key].get("ask")
        if bid is None:
            raise ExchangeRateNotFoundError(
                f"No bid/ask price in AwesomeAPI response for {base}->{quote}."
            )
        rate = Decimal(str(bid))
        _rate_cache[cache_key] = (rate, time.monotonic())
        return rate

    async def _fetch_rate_inverse(self, base: str, quote: str) -> Decimal:
        """Fallback: fetch quote->base and invert."""
        cache_key = f"{base.upper()}-{quote.upper()}"
        cached = _rate_cache.get(cache_key)
        if cached is not None:
            rate, fetched_at = cached
            if time.monotonic() - fetched_at < _CACHE_TTL_SECONDS:
                return rate

        url = _AWESOMEAPI_URL.format(base=quote.upper(), quote=base.upper())
        pair_key = f"{quote.upper()}{base.upper()}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except ExchangeRateNotFoundError:
            raise
        except Exception as exc:
            raise ExchangeRateNotFoundError(
                f"Live FX rate unavailable for inverse pair {quote}->{base}: {exc}"
            ) from exc

        if pair_key not in data:
            raise ExchangeRateNotFoundError(
                f"Pair {quote}->{base} not found in AwesomeAPI response."
            )
        bid = data[pair_key].get("bid") or data[pair_key].get("ask")
        if bid is None:
            raise ExchangeRateNotFoundError(
                f"No bid/ask price in AwesomeAPI inverse response for {quote}->{base}."
            )
        rate = Decimal("1") / Decimal(str(bid))
        _rate_cache[cache_key] = (rate, time.monotonic())
        return rate
