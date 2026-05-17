"""Tests for pricing strategies and resolver."""

from __future__ import annotations

from decimal import Decimal

import pytest

from srm_credit_engine.domain.exceptions import PricingStrategyNotFoundError
from srm_credit_engine.domain.pricing import (
    ChequePreDatadoStrategy,
    ContratoUsdStrategy,
    DuplicataMercantilStrategy,
    PricingStrategyResolver,
)
from srm_credit_engine.domain.value_objects.money import Money

BASE_RATE = Decimal("0.01")


def _approx(actual: Decimal, expected: Decimal, tol: str = "0.01") -> bool:
    return abs(actual - expected) <= Decimal(tol)


def test_duplicata_discounts_face_value_correctly() -> None:
    # FV=1000 BRL, 1 month, base=1% + spread=1.5% => effective=2.5%
    # PV = 1000 / 1.025 = 975.61
    result = DuplicataMercantilStrategy.price(
        Money(Decimal("1000.00"), "BRL"), Decimal("1"), BASE_RATE
    )
    assert result.present_value.currency == "BRL"
    assert _approx(result.present_value.amount, Decimal("975.61"))
    assert result.effective_monthly_rate == Decimal("0.025")
    assert result.spread_monthly == Decimal("0.015")


def test_cheque_uses_higher_spread() -> None:
    # FV=1000 BRL, 2 months, base=1% + spread=2.5% => effective=3.5%
    # PV = 1000 / 1.035^2 ≈ 933.51
    result = ChequePreDatadoStrategy.price(
        Money(Decimal("1000.00"), "BRL"), Decimal("2"), BASE_RATE
    )
    assert _approx(result.present_value.amount, Decimal("933.51"))
    assert result.spread_monthly == Decimal("0.025")


def test_contrato_usd_returns_usd_present_value() -> None:
    result = ContratoUsdStrategy.price(
        Money(Decimal("10000.00"), "USD"), Decimal("3"), BASE_RATE
    )
    assert result.present_value.currency == "USD"
    # base 1% + spread 1.2% = 2.2% ; PV = 10000 / 1.022^3 ≈ 9368.01
    assert _approx(result.present_value.amount, Decimal("9368.01"))


def test_zero_term_returns_face_value() -> None:
    result = DuplicataMercantilStrategy.price(
        Money(Decimal("500.00"), "BRL"), Decimal("0"), BASE_RATE
    )
    assert result.present_value.amount == Decimal("500.00")


def test_negative_term_rejected() -> None:
    with pytest.raises(ValueError, match="term_months"):
        DuplicataMercantilStrategy.price(
            Money(Decimal("500.00"), "BRL"), Decimal("-1"), BASE_RATE
        )


def test_negative_base_rate_rejected() -> None:
    with pytest.raises(ValueError, match="base_rate_monthly"):
        DuplicataMercantilStrategy.price(
            Money(Decimal("500.00"), "BRL"), Decimal("1"), Decimal("-0.01")
        )


def test_non_decimal_term_rejected() -> None:
    with pytest.raises(TypeError, match="term_months"):
        DuplicataMercantilStrategy.price(
            Money(Decimal("500.00"), "BRL"),
            1,  # type: ignore[arg-type]
            BASE_RATE,
        )


def test_resolver_returns_registered_strategy() -> None:
    resolver = PricingStrategyResolver()
    assert resolver.resolve("DUPLICATA_MERCANTIL") is DuplicataMercantilStrategy
    assert resolver.resolve("CHEQUE_PRE_DATADO") is ChequePreDatadoStrategy
    assert resolver.resolve("CONTRATO_USD") is ContratoUsdStrategy


def test_resolver_raises_for_unknown_product() -> None:
    resolver = PricingStrategyResolver()
    with pytest.raises(PricingStrategyNotFoundError):
        resolver.resolve("UNKNOWN_PRODUCT")


def test_resolver_supports_custom_registration() -> None:
    resolver = PricingStrategyResolver(strategies=[])
    resolver.register(DuplicataMercantilStrategy)
    assert resolver.available_codes() == ("DUPLICATA_MERCANTIL",)


def test_pricing_preserves_decimal_precision_on_large_values() -> None:
    # FV = 1,000,000.00 BRL, 12 months at base+spread 2.5%/m
    # Discount factor = 1.025^12 ≈ 1.34488882..., PV ≈ 743555.50
    result = DuplicataMercantilStrategy.price(
        Money(Decimal("1000000.00"), "BRL"), Decimal("12"), BASE_RATE
    )
    assert isinstance(result.present_value.amount, Decimal)
    assert _approx(result.present_value.amount, Decimal("743555.50"), tol="1.00")
