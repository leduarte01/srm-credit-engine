"""Money value object with strict decimal arithmetic for financial precision."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary amount tied to an ISO-4217 currency code.

    Uses :class:`decimal.Decimal` exclusively (never ``float``) to avoid
    precision loss in financial computations. Adopts banker's rounding
    (ROUND_HALF_EVEN) by default, the standard in financial systems.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money.amount must be a decimal.Decimal instance.")
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError("Currency must be an ISO-4217 three-letter code.")
        object.__setattr__(self, "currency", self.currency.upper())

    # ------------------------------------------------------------------ ops
    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: Decimal) -> Money:
        if not isinstance(factor, Decimal):
            raise TypeError("Multiplication factor must be Decimal.")
        return Money(self.amount * factor, self.currency)

    def quantize(self, places: int = 2) -> Money:
        """Round to N decimal places using banker's rounding."""
        quantum = Decimal(10) ** -places
        return Money(self.amount.quantize(quantum, rounding=ROUND_HALF_EVEN), self.currency)

    # ------------------------------------------------------------ internals
    def _ensure_same_currency(self, other: Money) -> None:
        if other.currency != self.currency:
            raise ValueError(
                f"Cannot operate on different currencies: {self.currency} vs {other.currency}"
            )

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
