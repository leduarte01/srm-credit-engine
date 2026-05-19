"""Concrete pricing strategies and a shared base implementation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from srm_credit_engine.domain.pricing.strategy import PricingResult
from srm_credit_engine.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class _CompoundDiscountStrategy:
    """Shared compound-discount implementation parametrised by ``code`` + spread."""

    code: str
    monthly_spread: Decimal

    def price(
        self,
        face_value: Money,
        term_months: Decimal,
        base_rate_monthly: Decimal,
    ) -> PricingResult:
        if not isinstance(term_months, Decimal):
            raise TypeError("term_months must be a decimal.Decimal.")
        if not isinstance(base_rate_monthly, Decimal):
            raise TypeError("base_rate_monthly must be a decimal.Decimal.")
        if term_months < 0:
            raise ValueError("term_months cannot be negative.")
        if base_rate_monthly < 0:
            raise ValueError("base_rate_monthly cannot be negative.")

        effective_rate = base_rate_monthly + self.monthly_spread
        discount_factor = (Decimal("1") + effective_rate) ** term_months
        pv_amount = face_value.amount / discount_factor
        present_value = Money(pv_amount, face_value.currency).quantize(2)

        return PricingResult(
            present_value=present_value,
            base_rate_monthly=base_rate_monthly,
            spread_monthly=self.monthly_spread,
            effective_monthly_rate=effective_rate,
            term_months=term_months,
        )


# ---------------------------------------------------------------- registry
# Codes must match the seed in db/migrations/V1__init.sql (product_type table).

DuplicataMercantilStrategy = _CompoundDiscountStrategy(
    code="DUPLICATA_MERCANTIL",
    monthly_spread=Decimal("0.15"),
)

ChequePreDatadoStrategy = _CompoundDiscountStrategy(
    code="CHEQUE_PRE_DATADO",
    monthly_spread=Decimal("0.025"),
)

ContratoUsdStrategy = _CompoundDiscountStrategy(
    code="CONTRATO_USD",
    monthly_spread=Decimal("0.012"),
)
