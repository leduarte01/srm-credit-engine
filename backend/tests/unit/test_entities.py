"""Tests for domain entities (Receivable, ExchangeRate, ProductType, Assignor, Currency)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from srm_credit_engine.domain.entities import (
    Assignor,
    Currency,
    ExchangeRate,
    ProductType,
    Receivable,
    ReceivableStatus,
)
from srm_credit_engine.domain.exceptions import (
    AlreadySettledError,
    InvalidReceivableError,
)
from srm_credit_engine.domain.value_objects.money import Money


# -------------------------------------------------------------- Currency
def test_currency_uppercases_code() -> None:
    c = Currency(code="brl", name="Real")
    assert c.code == "BRL"


def test_currency_rejects_bad_code() -> None:
    with pytest.raises(ValueError, match="ISO-4217"):
        Currency(code="BR", name="X")


# -------------------------------------------------------------- ProductType
def test_product_type_rejects_negative_spread() -> None:
    with pytest.raises(ValueError, match="negative"):
        ProductType(
            code="X", name="X", monthly_spread=Decimal("-0.01"), settlement_currency_code="BRL"
        )


def test_product_type_requires_decimal_spread() -> None:
    with pytest.raises(TypeError):
        ProductType(
            code="X",
            name="X",
            monthly_spread=0.01,  # type: ignore[arg-type]
            settlement_currency_code="BRL",
        )


# -------------------------------------------------------------- Assignor
def test_assignor_normalises_cnpj() -> None:
    a = Assignor(document="12.345.678/0001-90", legal_name="Acme")
    assert a.document == "12345678000190"


def test_assignor_rejects_invalid_cnpj_length() -> None:
    with pytest.raises(ValueError, match="14 digits"):
        Assignor(document="123", legal_name="Acme")


# -------------------------------------------------------------- ExchangeRate
def test_exchange_rate_rejects_same_currencies() -> None:
    with pytest.raises(ValueError, match="differ"):
        ExchangeRate(
            base_currency="USD",
            quote_currency="USD",
            rate=Decimal("1"),
            valid_from=datetime(2025, 1, 1, tzinfo=UTC),
        )


def test_exchange_rate_active_window() -> None:
    fr = ExchangeRate(
        base_currency="USD",
        quote_currency="BRL",
        rate=Decimal("5.0"),
        valid_from=datetime(2025, 1, 1, tzinfo=UTC),
        valid_to=datetime(2025, 6, 1, tzinfo=UTC),
    )
    assert fr.is_active_at(datetime(2025, 3, 1, tzinfo=UTC))
    assert not fr.is_active_at(datetime(2024, 12, 31, tzinfo=UTC))
    assert not fr.is_active_at(datetime(2025, 6, 1, tzinfo=UTC))  # half-open


def test_exchange_rate_open_ended() -> None:
    fr = ExchangeRate(
        base_currency="USD",
        quote_currency="BRL",
        rate=Decimal("5.0"),
        valid_from=datetime(2025, 1, 1, tzinfo=UTC),
    )
    assert fr.is_active_at(datetime(2099, 12, 31, tzinfo=UTC))


# -------------------------------------------------------------- Receivable
def _make_receivable(due_offset_days: int = 30) -> Receivable:
    issue = date(2025, 1, 1)
    return Receivable(
        assignor_document="12345678000190",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("1000.00"), "BRL"),
        issue_date=issue,
        due_date=issue + timedelta(days=due_offset_days),
        external_reference="NF-001",
    )


def test_receivable_rejects_due_before_issue() -> None:
    with pytest.raises(InvalidReceivableError, match="due_date"):
        Receivable(
            assignor_document="12345678000190",
            product_code="X",
            face_value=Money(Decimal("100"), "BRL"),
            issue_date=date(2025, 1, 10),
            due_date=date(2025, 1, 5),
            external_reference="A",
        )


def test_receivable_rejects_non_positive_face_value() -> None:
    with pytest.raises(InvalidReceivableError, match="face_value"):
        Receivable(
            assignor_document="12345678000190",
            product_code="X",
            face_value=Money(Decimal("0"), "BRL"),
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 2, 1),
            external_reference="A",
        )


def test_term_in_months_uses_30day_convention() -> None:
    r = _make_receivable(due_offset_days=60)
    assert r.term_in_months() == Decimal("2")


def test_term_zero_when_reference_past_due() -> None:
    r = _make_receivable(due_offset_days=30)
    assert r.term_in_months(date(2025, 3, 1)) == Decimal("0")


def test_mark_as_settled_bumps_version_and_blocks_double_settlement() -> None:
    r = _make_receivable()
    initial_version = r.version
    r.mark_as_settled()
    assert r.status is ReceivableStatus.SETTLED
    assert r.version == initial_version + 1
    with pytest.raises(AlreadySettledError):
        r.mark_as_settled()


def test_settle_then_cancel_rejected() -> None:
    r = _make_receivable()
    r.mark_as_settled()
    with pytest.raises(AlreadySettledError):
        r.cancel()


def test_cancel_then_price_rejected() -> None:
    r = _make_receivable()
    r.cancel()
    with pytest.raises(InvalidReceivableError):
        r.mark_as_priced()
