"""Live FX rate adapter — fetches real-time quotes from AwesomeAPI (BR).

End-point used: https://economia.awesomeapi.com.br/json/last/{BASE}-{QUOTE}
No authentication required. Free tier, no rate limit for low volume.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import httpx

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.observability.metrics import FX_LOOKUPS

_AWESOMEAPI_URL = "https://economia.awesomeapi.com.br/json/last/{base}-{quote}"
_TIMEOUT_SECONDS = 5.0


class LiveRateCurrencyConverter:
    """Fetches real-time FX rates from AwesomeAPI.

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
            except ExchangeRateNotFoundError:
                raise ExchangeRateNotFoundError(
                    f"Live FX rate unavailable for {base}->{quote}: {exc}"
                ) from exc

        if pair_key not in data:
            try:
                return await self._fetch_rate_inverse(base, quote)
            except ExchangeRateNotFoundError:
                raise ExchangeRateNotFoundError(
                    f"Pair {base}->{quote} not found in AwesomeAPI response."
                ) from None

        bid = data[pair_key].get("bid") or data[pair_key].get("ask")
        if bid is None:
            raise ExchangeRateNotFoundError(
                f"No bid/ask price in AwesomeAPI response for {base}->{quote}."
            )
        return Decimal(str(bid))

    async def _fetch_rate_inverse(self, base: str, quote: str) -> Decimal:
        """Fallback: fetch quote->base and invert."""
        url = _AWESOMEAPI_URL.format(base=quote.upper(), quote=base.upper())
        pair_key = f"{quote.upper()}{base.upper()}"
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        if pair_key not in data:
            raise ExchangeRateNotFoundError(
                f"Pair {quote}->{base} not found in AwesomeAPI response."
            )
        bid = data[pair_key].get("bid") or data[pair_key].get("ask")
        if bid is None:
            raise ExchangeRateNotFoundError(
                f"No bid/ask price in AwesomeAPI inverse response for {quote}->{base}."
            )
        return Decimal("1") / Decimal(str(bid))
