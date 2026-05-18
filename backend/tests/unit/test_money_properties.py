"""Property-based tests for the :class:`Money` value object.

These tests use :mod:`hypothesis` to assert algebraic invariants of
financial arithmetic (commutativity, identity, sign preservation) under a
wide range of randomly generated ``Decimal`` inputs.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from srm_credit_engine.domain.value_objects.money import Money

CURRENCIES = st.sampled_from(["BRL", "USD", "EUR", "GBP", "JPY"])

# Bounded positive decimals with up to 2 fractional digits to keep arithmetic
# representable and avoid pathological exponents.
POSITIVE_DECIMALS = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("1000000000.00"),
    allow_nan=False,
    allow_infinity=False,
    places=2,
)


@given(amount=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_constructor_preserves_amount_and_normalises_currency(
    amount: Decimal, currency: str
) -> None:
    m = Money(amount, currency.lower())
    assert m.amount == amount
    assert m.currency == currency.upper()


@given(a=POSITIVE_DECIMALS, b=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_addition_is_commutative(a: Decimal, b: Decimal, currency: str) -> None:
    left = Money(a, currency).add(Money(b, currency))
    right = Money(b, currency).add(Money(a, currency))
    assert left == right


@given(
    a=POSITIVE_DECIMALS,
    b=POSITIVE_DECIMALS,
    c=POSITIVE_DECIMALS,
    currency=CURRENCIES,
)
def test_addition_is_associative(a: Decimal, b: Decimal, c: Decimal, currency: str) -> None:
    left = Money(a, currency).add(Money(b, currency)).add(Money(c, currency))
    right = Money(a, currency).add(Money(b, currency).add(Money(c, currency)))
    assert left == right


@given(a=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_subtraction_inverts_addition(a: Decimal, currency: str) -> None:
    m = Money(a, currency)
    result = m.add(m).subtract(m)
    assert result == m


@given(amount=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_multiplication_by_one_is_identity(amount: Decimal, currency: str) -> None:
    m = Money(amount, currency)
    assert m.multiply(Decimal("1")) == m


@given(amount=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_multiplication_by_zero_yields_zero(amount: Decimal, currency: str) -> None:
    m = Money(amount, currency)
    assert m.multiply(Decimal("0")).amount == Decimal("0")


@given(amount=POSITIVE_DECIMALS, currency=CURRENCIES)
def test_quantize_is_idempotent(amount: Decimal, currency: str) -> None:
    once = Money(amount, currency).quantize(2)
    twice = once.quantize(2)
    assert once == twice


@given(
    a=POSITIVE_DECIMALS,
    b=POSITIVE_DECIMALS,
    c1=CURRENCIES,
    c2=CURRENCIES,
)
def test_addition_with_different_currencies_always_raises(
    a: Decimal, b: Decimal, c1: str, c2: str
) -> None:
    if c1 == c2:
        return  # nothing to assert in the matching case
    with pytest.raises(ValueError, match="different currencies"):
        Money(a, c1).add(Money(b, c2))


@given(
    a=POSITIVE_DECIMALS,
    b=POSITIVE_DECIMALS,
    c1=CURRENCIES,
    c2=CURRENCIES,
)
def test_subtraction_with_different_currencies_always_raises(
    a: Decimal, b: Decimal, c1: str, c2: str
) -> None:
    if c1 == c2:
        return
    with pytest.raises(ValueError, match="different currencies"):
        Money(a, c1).subtract(Money(b, c2))


def test_subtract_same_currency_works() -> None:
    result = Money(Decimal("10"), "BRL").subtract(Money(Decimal("4"), "BRL"))
    assert result == Money(Decimal("6"), "BRL")


def test_str_representation_contains_amount_and_currency() -> None:
    assert str(Money(Decimal("12.34"), "BRL")) == "12.34 BRL"


def test_quantize_with_three_places_keeps_precision() -> None:
    m = Money(Decimal("1.2345"), "USD").quantize(3)
    assert m.amount == Decimal("1.234")  # banker's rounding 1.2345 -> 1.234
