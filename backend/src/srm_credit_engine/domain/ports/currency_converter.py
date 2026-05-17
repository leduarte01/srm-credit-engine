"""Currency conversion port — implemented by infrastructure adapters."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from srm_credit_engine.domain.value_objects.money import Money


@runtime_checkable
class CurrencyConverter(Protocol):
    """Converts a :class:`Money` amount from one currency to another.

    Implementations resolve the appropriate FX rate (e.g. from the database
    using a temporal validity window, or from an external feed) and return
    a new :class:`Money` in the target currency.
    """

    async def convert(
        self,
        amount: Money,
        target_currency: str,
        at: datetime,
    ) -> Money: ...
