"""Property-based tests for the pricing strategies and service layer.

Asserts financial invariants that must hold for any face value, term and
spread combination — independent of dialect or product type.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable
from srm_credit_engine.domain.pricing.resolver import PricingStrategyResolver
from srm_credit_engine.domain.pricing.strategies import (
    ChequePreDatadoStrategy,
    ContratoUsdStrategy,
    DuplicataMercantilStrategy,
)
from srm_credit_engine.domain.services.pricing_service import PricingService
from srm_credit_engine.domain.value_objects.money import Money

STRATEGIES = [
    DuplicataMercantilStrategy,
    ChequePreDatadoStrategy,
    ContratoUsdStrategy,
]

POSITIVE_FACE = st.decimals(
    min_value=Decimal("1.00"),
    max_value=Decimal("10000000.00"),
    allow_nan=False,
    allow_infinity=False,
    places=2,
)
TERMS = st.decimals(
    min_value=Decimal("0.1"),
    max_value=Decimal("60"),
    allow_nan=False,
    allow_infinity=False,
    places=2,
)
BASE_RATES = st.decimals(
    min_value=Decimal("0"),
    max_value=Decimal("0.05"),
    allow_nan=False,
    allow_infinity=False,
    places=4,
)


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(face=POSITIVE_FACE, term=TERMS, base=BASE_RATES)
def test_present_value_never_exceeds_face_value(
    face: Decimal, term: Decimal, base: Decimal
) -> None:
    for strategy in STRATEGIES:
        result = strategy.price(Money(face, "BRL"), term, base)
        assert result.present_value.amount <= face


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(face=POSITIVE_FACE, term=TERMS, base=BASE_RATES)
def test_present_value_is_strictly_positive(face: Decimal, term: Decimal, base: Decimal) -> None:
    for strategy in STRATEGIES:
        result = strategy.price(Money(face, "BRL"), term, base)
        assert result.present_value.amount > 0


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(face=POSITIVE_FACE, term=TERMS, base=BASE_RATES)
def test_effective_rate_is_base_plus_spread(face: Decimal, term: Decimal, base: Decimal) -> None:
    for strategy in STRATEGIES:
        result = strategy.price(Money(face, "BRL"), term, base)
        assert result.effective_monthly_rate == base + result.spread_monthly


def test_strategy_rejects_non_decimal_term() -> None:
    with pytest.raises(TypeError, match="term_months"):
        DuplicataMercantilStrategy.price(Money(Decimal("100"), "BRL"), 1, Decimal("0.01"))  # type: ignore[arg-type]


def test_strategy_rejects_non_decimal_base_rate() -> None:
    with pytest.raises(TypeError, match="base_rate_monthly"):
        DuplicataMercantilStrategy.price(Money(Decimal("100"), "BRL"), Decimal("1"), 0.01)  # type: ignore[arg-type]


def test_strategy_rejects_negative_term() -> None:
    with pytest.raises(ValueError, match="term_months"):
        DuplicataMercantilStrategy.price(
            Money(Decimal("100"), "BRL"), Decimal("-1"), Decimal("0.01")
        )


def test_strategy_rejects_negative_base_rate() -> None:
    with pytest.raises(ValueError, match="base_rate_monthly"):
        DuplicataMercantilStrategy.price(
            Money(Decimal("100"), "BRL"), Decimal("1"), Decimal("-0.01")
        )


def test_pricing_service_rejects_non_decimal_base_rate() -> None:
    converter = _StubConverter()
    with pytest.raises(TypeError, match="base_rate_monthly"):
        PricingService(
            resolver=PricingStrategyResolver(),
            currency_converter=converter,
            base_rate_monthly=0.01,  # type: ignore[arg-type]
        )


@pytest.mark.asyncio
async def test_pricing_service_rejects_product_mismatch() -> None:
    service = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=_StubConverter(),
        base_rate_monthly=Decimal("0.01"),
    )
    receivable = Receivable(
        assignor_document="12345678000190",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("1000"), "BRL"),
        issue_date=date(2024, 1, 1),
        due_date=date(2024, 4, 1),
        external_reference="NF-MIS",
    )
    other_product = ProductType(
        code="CHEQUE_PRE_DATADO",
        name="Cheque",
        monthly_spread=Decimal("0.02"),
        settlement_currency_code="BRL",
    )
    with pytest.raises(ValueError, match="Product mismatch"):
        await service.price(receivable, other_product, date(2024, 2, 1), datetime(2024, 2, 1))


@pytest.mark.asyncio
async def test_pricing_service_skips_fx_when_currencies_match() -> None:
    converter = _StubConverter(should_fail=True)
    service = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=converter,
        base_rate_monthly=Decimal("0.01"),
    )
    receivable = Receivable(
        assignor_document="12345678000190",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("1000"), "BRL"),
        issue_date=date(2024, 1, 1),
        due_date=date(2024, 4, 1),
        external_reference="NF-SAME",
    )
    product = ProductType(
        code="DUPLICATA_MERCANTIL",
        name="Duplicata",
        monthly_spread=Decimal("0.015"),
        settlement_currency_code="BRL",
    )
    priced = await service.price(receivable, product, date(2024, 1, 1), datetime(2024, 2, 1))
    assert priced.fx_rate_applied is None
    assert priced.settlement_value.currency == "BRL"
    assert converter.calls == 0  # FX path was not invoked


class _StubConverter:
    """Minimal :class:`CurrencyConverter` stub for unit tests."""

    def __init__(self, *, should_fail: bool = False) -> None:
        self.calls = 0
        self._should_fail = should_fail

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        self.calls += 1
        if self._should_fail:
            raise AssertionError("converter should not be invoked")
        # Trivial 1:1 conversion just changes the currency label.
        return Money(amount.amount, target_currency)
