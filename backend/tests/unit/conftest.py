"""Pytest fixtures providing an in-memory aiosqlite engine for infra tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from srm_credit_engine.infrastructure.models import (
    Base,
    CurrencyORM,
    ExchangeRateORM,
    ProductTypeORM,
)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as sess:
        # Seed minimal reference data shared across all infra tests.
        sess.add_all(
            [
                CurrencyORM(code="BRL", name="Real", decimal_places=2),
                CurrencyORM(code="USD", name="US Dollar", decimal_places=2),
            ]
        )
        await sess.flush()
        sess.add_all(
            [
                ProductTypeORM(
                    code="DUPLICATA_MERCANTIL",
                    name="Duplicata Mercantil",
                    monthly_spread=Decimal("0.015"),
                    settlement_currency_code="BRL",
                ),
                ProductTypeORM(
                    code="CONTRATO_USD",
                    name="Contrato USD",
                    monthly_spread=Decimal("0.012"),
                    settlement_currency_code="USD",
                ),
                ExchangeRateORM(
                    id=uuid4(),
                    base_currency="USD",
                    quote_currency="BRL",
                    rate=Decimal("5.05"),
                    valid_from=datetime(2024, 1, 1, tzinfo=UTC),
                    valid_to=None,
                ),
            ]
        )
        await sess.commit()
        yield sess

    await engine.dispose()


@pytest.fixture
def utc_now() -> datetime:
    return datetime(2025, 1, 15, 12, 0, tzinfo=UTC)
