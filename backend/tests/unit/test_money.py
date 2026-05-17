"""Unit tests for Money value object."""

from __future__ import annotations

from decimal import Decimal

import pytest

from srm_credit_engine.domain.value_objects.money import Money


def test_creates_money_with_decimal_amount() -> None:
    m = Money(Decimal("100.50"), "BRL")
    assert m.amount == Decimal("100.50")
    assert m.currency == "BRL"


def test_currency_is_uppercased() -> None:
    assert Money(Decimal("1"), "usd").currency == "USD"


def test_rejects_float_amount() -> None:
    with pytest.raises(TypeError):
        Money(100.50, "BRL")  # type: ignore[arg-type]


def test_rejects_invalid_currency() -> None:
    with pytest.raises(ValueError, match="ISO-4217"):
        Money(Decimal("1"), "REAL")


def test_addition_same_currency() -> None:
    result = Money(Decimal("10"), "BRL").add(Money(Decimal("5"), "BRL"))
    assert result == Money(Decimal("15"), "BRL")


def test_addition_different_currency_raises() -> None:
    with pytest.raises(ValueError, match="different currencies"):
        Money(Decimal("10"), "BRL").add(Money(Decimal("5"), "USD"))


def test_multiplication_requires_decimal_factor() -> None:
    with pytest.raises(TypeError):
        Money(Decimal("10"), "BRL").multiply(2)  # type: ignore[arg-type]


def test_quantize_uses_bankers_rounding() -> None:
    # 0.125 -> 0.12 (banker's rounding: round half to even)
    assert Money(Decimal("0.125"), "BRL").quantize(2).amount == Decimal("0.12")
    # 0.135 -> 0.14
    assert Money(Decimal("0.135"), "BRL").quantize(2).amount == Decimal("0.14")


def test_money_is_immutable() -> None:
    m = Money(Decimal("1"), "BRL")
    with pytest.raises(AttributeError):
        m.amount = Decimal("2")  # type: ignore[misc]
