"""Concrete SQLAlchemy repositories implementing the domain ports."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.entities.exchange_rate import ExchangeRate
from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable
from srm_credit_engine.domain.entities.settlement import Settlement
from srm_credit_engine.domain.exceptions import (
    ConcurrencyConflictError,
    ReceivableNotFoundError,
)
from srm_credit_engine.domain.ports.repositories import Page, ReceivableFilter
from srm_credit_engine.infrastructure import mappers
from srm_credit_engine.infrastructure.models import (
    AssignorORM,
    ExchangeRateORM,
    ProductTypeORM,
    ReceivableORM,
    SettlementEventORM,
    SettlementORM,
)


class SqlAlchemyAssignorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, assignor_id: UUID) -> Assignor | None:
        row = await self._session.get(AssignorORM, assignor_id)
        return mappers.to_assignor(row) if row is not None else None

    async def get_by_document(self, document: str) -> Assignor | None:
        stmt = select(AssignorORM).where(AssignorORM.document == document)
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return mappers.to_assignor(row) if row is not None else None

    async def get_id_by_document(self, document: str) -> UUID | None:
        stmt = select(AssignorORM.id).where(AssignorORM.document == document)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add(self, assignor: Assignor) -> UUID:
        row = AssignorORM(document=assignor.document, legal_name=assignor.legal_name)
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ConcurrencyConflictError(
                f"Assignor with document {assignor.document} already exists."
            ) from exc
        return row.id

    async def list(self, offset: int = 0, limit: int = 50) -> Page[Assignor]:
        total = await self._session.scalar(select(func.count()).select_from(AssignorORM)) or 0
        stmt = (
            select(AssignorORM)
            .order_by(AssignorORM.legal_name)
            .offset(offset)
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        items = [mappers.to_assignor(r) for r in rows]
        return Page(items=items, total=int(total), offset=offset, limit=limit)


class SqlAlchemyProductTypeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_code(self, code: str) -> ProductType | None:
        row = await self._session.get(ProductTypeORM, code)
        return mappers.to_product_type(row) if row is not None else None

    async def list_all(self) -> list[ProductType]:
        rows = (await self._session.execute(select(ProductTypeORM))).scalars().all()
        return [mappers.to_product_type(r) for r in rows]


class SqlAlchemyExchangeRateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(
        self, base_currency: str, quote_currency: str, at: datetime
    ) -> ExchangeRate | None:
        stmt = (
            select(ExchangeRateORM)
            .where(
                ExchangeRateORM.base_currency == base_currency,
                ExchangeRateORM.quote_currency == quote_currency,
                ExchangeRateORM.valid_from <= at,
            )
            .order_by(ExchangeRateORM.valid_from.desc())
            .limit(1)
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        rate = mappers.to_exchange_rate(row)
        return rate if rate.is_active_at(at) else None

    async def add(self, rate: ExchangeRate) -> UUID:
        row = ExchangeRateORM(
            base_currency=rate.base_currency,
            quote_currency=rate.quote_currency,
            rate=rate.rate,
            valid_from=rate.valid_from,
            valid_to=rate.valid_to,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ConcurrencyConflictError(
                f"Exchange rate {rate.base_currency}->{rate.quote_currency} "
                f"valid_from={rate.valid_from.isoformat()} conflicts with existing row."
            ) from exc
        return row.id

    async def list_history(
        self, base_currency: str, quote_currency: str
    ) -> list[ExchangeRate]:
        stmt = (
            select(ExchangeRateORM)
            .where(
                ExchangeRateORM.base_currency == base_currency,
                ExchangeRateORM.quote_currency == quote_currency,
            )
            .order_by(ExchangeRateORM.valid_from.desc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [mappers.to_exchange_rate(r) for r in rows]


class SqlAlchemyReceivableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _load_orm(self, receivable_id: UUID) -> ReceivableORM | None:
        return await self._session.get(ReceivableORM, receivable_id)

    async def get_by_id(self, receivable_id: UUID) -> Receivable | None:
        row = await self._load_orm(receivable_id)
        if row is None:
            return None
        assignor = await self._session.get(AssignorORM, row.assignor_id)
        if assignor is None:
            raise ReceivableNotFoundError(
                f"Assignor {row.assignor_id} missing for receivable {receivable_id}."
            )
        return mappers.to_receivable(row, assignor.document)

    async def add(self, receivable: Receivable, assignor_id: UUID) -> UUID:
        row = ReceivableORM(
            id=receivable.id,
            assignor_id=assignor_id,
            product_code=receivable.product_code,
            face_value_amount=receivable.face_value.amount,
            face_value_currency=receivable.face_value.currency,
            issue_date=receivable.issue_date,
            due_date=receivable.due_date,
            external_reference=receivable.external_reference,
            status=receivable.status.value,
            version=receivable.version,
            created_at=datetime.now(UTC),
        )
        self._session.add(row)
        await self._session.flush()
        return row.id

    async def update(self, receivable: Receivable) -> None:
        """Persist a receivable using optimistic locking on ``version``.

        Raises :class:`ConcurrencyConflictError` if the row was modified by
        another transaction between read and write.
        """
        row = await self._load_orm(receivable.id)
        if row is None:
            raise ReceivableNotFoundError(f"Receivable {receivable.id} not found.")
        expected_version = receivable.version - 1
        if row.version != expected_version:
            raise ConcurrencyConflictError(
                f"Receivable {receivable.id} version mismatch: "
                f"expected {expected_version}, found {row.version}."
            )
        row.status = receivable.status.value
        row.version = receivable.version
        await self._session.flush()

    async def list(
        self,
        filters: ReceivableFilter,
        offset: int = 0,
        limit: int = 50,
    ) -> Page[Receivable]:
        """Paginated listing of receivables with composable filters."""
        base_stmt = select(ReceivableORM).join(
            AssignorORM, ReceivableORM.assignor_id == AssignorORM.id
        )
        count_stmt = select(func.count()).select_from(ReceivableORM).join(
            AssignorORM, ReceivableORM.assignor_id == AssignorORM.id
        )

        conditions = []
        if filters.assignor_document is not None:
            conditions.append(AssignorORM.document == filters.assignor_document)
        if filters.product_code is not None:
            conditions.append(ReceivableORM.product_code == filters.product_code)
        if filters.status is not None:
            conditions.append(ReceivableORM.status == filters.status.value)
        if filters.currency is not None:
            conditions.append(ReceivableORM.face_value_currency == filters.currency)
        if filters.due_from is not None:
            conditions.append(ReceivableORM.due_date >= filters.due_from)
        if filters.due_to is not None:
            conditions.append(ReceivableORM.due_date <= filters.due_to)

        if conditions:
            base_stmt = base_stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = await self._session.scalar(count_stmt) or 0
        stmt = (
            base_stmt.order_by(ReceivableORM.due_date.asc(), ReceivableORM.id)
            .offset(offset)
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()

        # Pre-load assignors in one batch to avoid N+1.
        assignor_ids = {r.assignor_id for r in rows}
        assignors_stmt = select(AssignorORM).where(AssignorORM.id.in_(assignor_ids))
        assignor_map = {
            a.id: a.document
            for a in (await self._session.execute(assignors_stmt)).scalars().all()
        }
        items = [mappers.to_receivable(r, assignor_map[r.assignor_id]) for r in rows]
        return Page(items=items, total=int(total), offset=offset, limit=limit)


class SqlAlchemySettlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, settlement: Settlement) -> UUID:
        row = SettlementORM(
            id=settlement.id,
            receivable_id=settlement.receivable_id,
            discounted_amount=settlement.discounted_value.amount,
            settlement_currency=settlement.settlement_currency,
            settled_at=settlement.settled_at,
            base_rate_monthly=settlement.base_rate_monthly,
            spread_monthly=settlement.spread_monthly,
            term_months=settlement.term_months,
            fx_rate_applied=settlement.fx_rate_applied,
            version=settlement.version,
        )
        for event in settlement.events:
            row.events.append(
                SettlementEventORM(
                    id=event.id,
                    event_type=event.event_type.value,
                    occurred_at=event.occurred_at,
                    actor=event.actor,
                    payload=event.payload,
                )
            )
        self._session.add(row)
        await self._session.flush()
        return row.id

    async def get_by_id(self, settlement_id: UUID) -> Settlement | None:
        row = await self._session.get(SettlementORM, settlement_id)
        return mappers.to_settlement(row) if row is not None else None

    async def get_one(self, settlement_id: UUID) -> Settlement:
        row = await self._session.get(SettlementORM, settlement_id)
        if row is None:
            raise NoResultFound(f"Settlement {settlement_id} not found.")
        return mappers.to_settlement(row)
