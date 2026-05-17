"""Repository tests against the in-memory aiosqlite schema."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.entities.receivable import Receivable, ReceivableStatus
from srm_credit_engine.domain.entities.settlement import (
    Settlement,
    SettlementEvent,
    SettlementEventType,
)
from srm_credit_engine.domain.exceptions import (
    ConcurrencyConflictError,
    ReceivableNotFoundError,
)
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.infrastructure.repositories import (
    SqlAlchemyAssignorRepository,
    SqlAlchemyExchangeRateRepository,
    SqlAlchemyProductTypeRepository,
    SqlAlchemyReceivableRepository,
    SqlAlchemySettlementRepository,
)


async def test_assignor_round_trip(session: AsyncSession) -> None:
    repo = SqlAlchemyAssignorRepository(session)
    new_id = await repo.add(Assignor(document="12345678000199", legal_name="ACME LTDA"))
    found = await repo.get_by_id(new_id)
    assert found is not None
    assert found.document == "12345678000199"
    assert (await repo.get_by_document("12345678000199")) is not None


async def test_assignor_unique_document(session: AsyncSession) -> None:
    repo = SqlAlchemyAssignorRepository(session)
    await repo.add(Assignor(document="98765432000100", legal_name="Foo"))
    with pytest.raises(ConcurrencyConflictError):
        await repo.add(Assignor(document="98765432000100", legal_name="Bar"))


async def test_product_type_list(session: AsyncSession) -> None:
    repo = SqlAlchemyProductTypeRepository(session)
    products = await repo.list_all()
    codes = {p.code for p in products}
    assert {"DUPLICATA_MERCANTIL", "CONTRATO_USD"} <= codes


async def test_exchange_rate_active_pick(session: AsyncSession, utc_now: datetime) -> None:
    repo = SqlAlchemyExchangeRateRepository(session)
    rate = await repo.get_active("USD", "BRL", utc_now)
    assert rate is not None
    assert rate.rate == Decimal("5.05")
    assert (await repo.get_active("USD", "BRL", datetime(2020, 1, 1, tzinfo=UTC))) is None


async def test_receivable_optimistic_locking(session: AsyncSession) -> None:
    assignor_repo = SqlAlchemyAssignorRepository(session)
    assignor_id = await assignor_repo.add(
        Assignor(document="11111111000111", legal_name="Cedente A")
    )
    repo = SqlAlchemyReceivableRepository(session)
    receivable = Receivable(
        assignor_document="11111111000111",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("10000.00"), "BRL"),
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 4, 1),
        external_reference="NF-0001",
    )
    new_id = await repo.add(receivable, assignor_id)

    fetched = await repo.get_by_id(new_id)
    assert fetched is not None
    fetched.mark_as_priced()
    await repo.update(fetched)

    # Stale copy bumping version again should be rejected.
    stale = Receivable(
        assignor_document="11111111000111",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("10000.00"), "BRL"),
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 4, 1),
        external_reference="NF-0001",
        id=new_id,
        status=ReceivableStatus.PRICED,
        version=2,  # same as DB now, so next update expects version=1 — conflict
    )
    stale.mark_as_settled()  # bumps to 3, expects 2 in DB but DB has 2; OK
    await repo.update(stale)  # this should succeed
    # Now a truly stale write must fail:
    stale_bad = Receivable(
        assignor_document="11111111000111",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("10000.00"), "BRL"),
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 4, 1),
        external_reference="NF-0001",
        id=new_id,
        status=ReceivableStatus.SETTLED,
        version=2,  # tries to write expecting DB at v1, but DB is v3
    )
    with pytest.raises(ConcurrencyConflictError):
        await repo.update(stale_bad)


async def test_update_missing_receivable(session: AsyncSession) -> None:
    repo = SqlAlchemyReceivableRepository(session)
    ghost = Receivable(
        assignor_document="11111111000111",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("100.00"), "BRL"),
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 2, 1),
        external_reference="NF-X",
    )
    with pytest.raises(ReceivableNotFoundError):
        await repo.update(ghost)


async def test_settlement_round_trip_with_events(session: AsyncSession) -> None:
    assignor_repo = SqlAlchemyAssignorRepository(session)
    assignor_id = await assignor_repo.add(
        Assignor(document="22222222000122", legal_name="Cedente B")
    )
    receivables = SqlAlchemyReceivableRepository(session)
    receivable = Receivable(
        assignor_document="22222222000122",
        product_code="DUPLICATA_MERCANTIL",
        face_value=Money(Decimal("5000.00"), "BRL"),
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 3, 1),
        external_reference="NF-S-01",
    )
    receivable_id = await receivables.add(receivable, assignor_id)

    settlement = Settlement(
        receivable_id=receivable_id,
        discounted_value=Money(Decimal("4800.00"), "BRL"),
        settlement_currency="BRL",
        settled_at=datetime(2025, 1, 15, tzinfo=UTC),
        base_rate_monthly=Decimal("0.01"),
        spread_monthly=Decimal("0.015"),
        term_months=Decimal("2"),
    )
    settlement.append_event(
        SettlementEvent(
            event_type=SettlementEventType.CREATED,
            occurred_at=datetime(2025, 1, 15, tzinfo=UTC),
            actor="tester",
            payload={"reason": "unit-test"},
        )
    )
    repo = SqlAlchemySettlementRepository(session)
    new_id = await repo.add(settlement)
    await session.commit()

    loaded = await repo.get_by_id(new_id)
    assert loaded is not None
    assert loaded.discounted_value.amount == Decimal("4800.0000")
    assert len(loaded.events) == 1
    assert loaded.events[0].event_type is SettlementEventType.CREATED
    assert loaded.events[0].payload == {"reason": "unit-test"}
