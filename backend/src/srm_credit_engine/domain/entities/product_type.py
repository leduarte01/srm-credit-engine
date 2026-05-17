"""Product type reference entity carrying the monthly spread for pricing."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ProductType:
    """Catalogued credit product (e.g. Duplicata Mercantil, Cheque Pre-datado).

    The ``monthly_spread`` is the risk premium added to the base monthly rate
    when discounting receivables of this product.
    """

    code: str
    name: str
    monthly_spread: Decimal
    settlement_currency_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.monthly_spread, Decimal):
            raise TypeError("monthly_spread must be a decimal.Decimal.")
        if self.monthly_spread < 0:
            raise ValueError("monthly_spread cannot be negative.")
        if not self.code:
            raise ValueError("ProductType.code is required.")
