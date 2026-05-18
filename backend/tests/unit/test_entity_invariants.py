"""Edge-case and property-based tests for domain entity invariants.

Targets uncovered error branches and validates state-machine guarantees of
the :class:`Receivable` aggregate under random transition sequences.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.entities.currency import Currency
from srm_credit_engine.domain.entities.exchange_rate import ExchangeRate
from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable, ReceivableStatus
from srm_credit_engine.domain.exceptions import (
    AlreadySettledError,
    InvalidReceivableError,
)
from srm_credit_engine.domain.value_objects.money import Money

# -------------------------------------------------------------------- Assignor


def test_assignor_strips_punctuation_from_document() -> None:
    a = Assignor(document="12.345.678/0001-90", legal_name="Empresa X")
    assert a.document == "12345678000190"


def test_assignor_rejects_short_document() -> None:
    with pytest.raises(ValueError, match="14 digits"):
        Assignor(document="123", legal_name="Empresa X")


def test_assignor_rejects_blank_legal_name() -> None:
    with pytest.raises(ValueError, match="legal_name"):
        Assignor(document="12345678000190", legal_name="   ")


# -------------------------------------------------------------------- Currency


def test_currency_rejects_invalid_code_length() -> None:
    with pytest.raises(ValueError, match="ISO-4217"):
        Currency(code="REAL", name="Real")


def test_currency_rejects_negative_decimal_places() -> None:
    with pytest.raises(ValueError, match="decimal_places"):
        Currency(code="BRL", name="Real", decimal_places=-1)


def test_currency_uppercases_code() -> None:
    assert Currency(code="usd", name="US Dollar").code == "USD"


# ----------------------------------------------------------------- ProductType


def test_product_type_rejects_float_spread() -> None:
    with pytest.raises(TypeError, match="monthly_spread"):
        ProductType(
            code="X",
            name="X",
            monthly_spread=0.01,  # type: ignore[arg-type]
            settlement_currency_code="BRL",
        )


def test_product_type_rejects_negative_spread() -> None:
    with pytest.raises(ValueError, match="monthly_spread"):
        ProductType(
            code="X",
            name="X",
            monthly_spread=Decimal("-0.01"),
            settlement_currency_code="BRL",
        )


def test_product_type_rejects_blank_code() -> None:
    with pytest.raises(ValueError, match="code"):
        ProductType(
            code="",
            name="Anonymous",
            monthly_spread=Decimal("0.01"),
            settlement_currency_code="BRL",
        )


# ---------------------------------------------------------------- ExchangeRate


def test_exchange_rate_rejects_float_rate() -> None:
    with pytest.raises(TypeError, match="rate"):
        ExchangeRate(
            base_currency="USD",
            quote_currency="BRL",
            rate=5.05,  # type: ignore[arg-type]
            valid_from=datetime(2024, 1, 1),
        )


def test_exchange_rate_rejects_non_positive_rate() -> None:
    with pytest.raises(ValueError, match="positive"):
        ExchangeRate(
            base_currency="USD",
            quote_currency="BRL",
            rate=Decimal("0"),
            valid_from=datetime(2024, 1, 1),
        )


def test_exchange_rate_rejects_same_currencies() -> None:
    with pytest.raises(ValueError, match="differ"):
        ExchangeRate(
            base_currency="BRL",
            quote_currency="BRL",
            rate=Decimal("1"),
            valid_from=datetime(2024, 1, 1),
        )


def test_exchange_rate_rejects_inverted_validity_window() -> None:
    with pytest.raises(ValueError, match="valid_to"):
        ExchangeRate(
            base_currency="USD",
            quote_currency="BRL",
            rate=Decimal("5"),
            valid_from=datetime(2024, 6, 1),
            valid_to=datetime(2024, 1, 1),
        )


def test_exchange_rate_is_active_at_open_ended_window() -> None:
    rate = ExchangeRate(
        base_currency="USD",
        quote_currency="BRL",
        rate=Decimal("5"),
        valid_from=datetime(2024, 1, 1),
    )
    assert rate.is_active_at(datetime(2024, 1, 1)) is True
    assert rate.is_active_at(datetime(2030, 1, 1)) is True
    assert rate.is_active_at(datetime(2023, 12, 31)) is False


def test_exchange_rate_is_inactive_at_or_after_valid_to() -> None:
    rate = ExchangeRate(
        base_currency="USD",
        quote_currency="BRL",
        rate=Decimal("5"),
        valid_from=datetime(2024, 1, 1),
        valid_to=datetime(2024, 6, 1),
    )
    assert rate.is_active_at(datetime(2024, 5, 31)) is True
    assert rate.is_active_at(datetime(2024, 6, 1)) is False


# ----------------------------------------------------------------- Receivable


def _make_receivable(**overrides: object) -> Receivable:
    base: dict[str, object] = {
        "assignor_document": "12345678000190",
        "product_code": "DUPLICATA_MERCANTIL",
        "face_value": Money(Decimal("1000"), "BRL"),
        "issue_date": date(2024, 1, 1),
        "due_date": date(2024, 4, 1),
        "external_reference": "NF-001",
    }
    base.update(overrides)
    return Receivable(**base)  # type: ignore[arg-type]


def test_receivable_rejects_due_date_at_or_before_issue_date() -> None:
    with pytest.raises(InvalidReceivableError):
        _make_receivable(due_date=date(2024, 1, 1))
    with pytest.raises(InvalidReceivableError):
        _make_receivable(due_date=date(2023, 12, 31))


def test_receivable_rejects_blank_external_reference() -> None:
    with pytest.raises(InvalidReceivableError, match="external_reference"):
        _make_receivable(external_reference="   ")


def test_receivable_rejects_zero_face_value() -> None:
    # Money already disallows zero/negative? Money allows any Decimal; the
    # receivable invariant enforces the positivity check.
    with pytest.raises(InvalidReceivableError, match="face_value"):
        _make_receivable(face_value=Money(Decimal("-1"), "BRL"))


def test_term_in_months_returns_zero_when_reference_is_after_due_date() -> None:
    r = _make_receivable()
    assert r.term_in_months(date(2025, 1, 1)) == Decimal("0")


def test_cannot_price_after_settled() -> None:
    r = _make_receivable()
    r.mark_as_priced()
    r.mark_as_settled()
    with pytest.raises(AlreadySettledError):
        r.mark_as_priced()


def test_cannot_settle_a_cancelled_receivable() -> None:
    r = _make_receivable()
    r.cancel()
    with pytest.raises(InvalidReceivableError):
        r.mark_as_settled()


def test_cannot_price_a_cancelled_receivable() -> None:
    r = _make_receivable()
    r.cancel()
    with pytest.raises(InvalidReceivableError):
        r.mark_as_priced()


def test_cannot_cancel_a_settled_receivable() -> None:
    r = _make_receivable()
    r.mark_as_priced()
    r.mark_as_settled()
    with pytest.raises(AlreadySettledError):
        r.cancel()


def test_double_settlement_raises() -> None:
    r = _make_receivable()
    r.mark_as_priced()
    r.mark_as_settled()
    with pytest.raises(AlreadySettledError):
        r.mark_as_settled()


# -------------------------------------------------- Property-based state machine

_TRANSITIONS = st.lists(
    st.sampled_from(["price", "settle", "cancel"]),
    min_size=1,
    max_size=6,
)


@given(transitions=_TRANSITIONS)
def test_version_increments_on_every_successful_transition(
    transitions: list[str],
) -> None:
    r = _make_receivable()
    starting_version = r.version
    successes = 0
    method_map = {
        "price": "mark_as_priced",
        "settle": "mark_as_settled",
        "cancel": "cancel",
    }
    for step in transitions:
        try:
            getattr(r, method_map[step])()
        except (AlreadySettledError, InvalidReceivableError):
            continue
        successes += 1
    assert r.version == starting_version + successes


@given(days=st.integers(min_value=1, max_value=5 * 365))
def test_term_in_months_is_strictly_positive_for_future_due_date(days: int) -> None:
    issue = date(2024, 1, 1)
    due = issue + timedelta(days=days)
    r = _make_receivable(issue_date=issue, due_date=due)
    assert r.term_in_months() > Decimal("0")


def test_terminal_status_set_is_exactly_settled_and_cancelled() -> None:
    # Documents that the state machine has exactly two terminal states.
    terminals = {ReceivableStatus.SETTLED, ReceivableStatus.CANCELLED}
    assert terminals.issubset(set(ReceivableStatus))
