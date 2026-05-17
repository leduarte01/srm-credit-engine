"""Exchange rate entity with temporal validity window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    """FX rate from ``base_currency`` to ``quote_currency``.

    The rate is ``1 base = rate * quote``. Temporal validity is half-open:
    ``[valid_from, valid_to)`` — ``valid_to`` ``None`` means open-ended.
    """

    base_currency: str
    quote_currency: str
    rate: Decimal
    valid_from: datetime
    valid_to: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Decimal):
            raise TypeError("ExchangeRate.rate must be a decimal.Decimal.")
        if self.rate <= 0:
            raise ValueError("ExchangeRate.rate must be positive.")
        if self.base_currency == self.quote_currency:
            raise ValueError("base_currency and quote_currency must differ.")
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be strictly greater than valid_from.")

    def is_active_at(self, moment: datetime) -> bool:
        if moment < self.valid_from:
            return False
        return self.valid_to is None or moment < self.valid_to
