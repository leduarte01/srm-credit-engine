"""Pricing strategy protocol and result DTO."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable

from srm_credit_engine.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class PricingResult:
    """Outcome of a pricing computation.

    ``present_value`` is the amount the fund pays today for the receivable.
    ``effective_monthly_rate`` is ``base_rate + spread`` applied per month.
    """

    present_value: Money
    base_rate_monthly: Decimal
    spread_monthly: Decimal
    effective_monthly_rate: Decimal
    term_months: Decimal


@runtime_checkable
class PricingStrategy(Protocol):
    """Discounts the face value of a receivable into a present value.

    Concrete strategies declare their ``code`` (matching ``ProductType.code``)
    and the ``monthly_spread`` charged on top of the base rate. The discount
    formula is ``PV = FV / (1 + base + spread) ** term_months``.
    """

    code: str
    monthly_spread: Decimal

    def price(
        self,
        face_value: Money,
        term_months: Decimal,
        base_rate_monthly: Decimal,
    ) -> PricingResult: ...
