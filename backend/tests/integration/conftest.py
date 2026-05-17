"""Shared fixtures for integration tests against the FastAPI app."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from srm_credit_engine.infrastructure.database import get_session
from srm_credit_engine.infrastructure.models import (
    AssignorORM,
    Base,
    CurrencyORM,
    ExchangeRateORM,
    ProductTypeORM,
)
from srm_credit_engine.main import create_app


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=eng, expire_on_commit=False, class_=AsyncSession)
    async with factory() as sess:
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
                AssignorORM(
                    id=uuid4(),
                    document="12345678000190",
                    legal_name="Empresa Exemplo Ltda",
                ),
            ]
        )
        await sess.commit()
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    """FastAPI app wired to the in-memory test engine via dependency override."""
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session, session.begin():
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded_assignor(engine: AsyncEngine) -> dict[str, Any]:
    """Return the document of the seeded assignor."""
    return {"document": "12345678000190", "legal_name": "Empresa Exemplo Ltda"}
