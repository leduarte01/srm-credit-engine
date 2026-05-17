"""Tests for the database-backed currency converter adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.infrastructure.database_currency_converter import (
    DatabaseCurrencyConverter,
)
from srm_credit_engine.infrastructure.repositories import SqlAlchemyExchangeRateRepository


async def test_passthrough_when_currencies_match(session: AsyncSession) -> None:
    converter = DatabaseCurrencyConverter(SqlAlchemyExchangeRateRepository(session))
    amount = Money(Decimal("100"), "BRL")
    result = await converter.convert(amount, "BRL", datetime(2025, 1, 1, tzinfo=UTC))
    assert result is amount


async def test_direct_rate_conversion(session: AsyncSession) -> None:
    converter = DatabaseCurrencyConverter(SqlAlchemyExchangeRateRepository(session))
    result = await converter.convert(
        Money(Decimal("100"), "USD"), "BRL", datetime(2025, 1, 1, tzinfo=UTC)
    )
    assert result.currency == "BRL"
    assert result.amount == Decimal("505.00000000")


async def test_inverse_rate_fallback(session: AsyncSession) -> None:
    converter = DatabaseCurrencyConverter(SqlAlchemyExchangeRateRepository(session))
    # Seed has only USD->BRL; BRL->USD is computed via 1/5.05.
    result = await converter.convert(
        Money(Decimal("505"), "BRL"), "USD", datetime(2025, 1, 1, tzinfo=UTC)
    )
    assert result.currency == "USD"
    # 505 / 5.05 = 100.00000000
    assert result.amount == Decimal("100.00000000")


async def test_missing_rate_raises(session: AsyncSession) -> None:
    converter = DatabaseCurrencyConverter(SqlAlchemyExchangeRateRepository(session))
    with pytest.raises(ExchangeRateNotFoundError):
        await converter.convert(
            Money(Decimal("100"), "BRL"), "USD", datetime(2020, 1, 1, tzinfo=UTC)
        )
