"""Mappers between SQLAlchemy ORM rows and pure domain entities/aggregates."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.entities.exchange_rate import ExchangeRate
from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable, ReceivableStatus
from srm_credit_engine.domain.entities.settlement import (
    Settlement,
    SettlementEvent,
    SettlementEventType,
)
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.infrastructure.models import (
    AssignorORM,
    ExchangeRateORM,
    ProductTypeORM,
    ReceivableORM,
    SettlementEventORM,
    SettlementORM,
)


def _utc(value: datetime) -> datetime:
    """Coerce naive datetimes coming from SQLite to UTC-aware ones."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


# ----------------------------------------------------------------- Assignor
def to_assignor(row: AssignorORM) -> Assignor:
    return Assignor(document=row.document, legal_name=row.legal_name)


# -------------------------------------------------------------- ProductType
def to_product_type(row: ProductTypeORM) -> ProductType:
    return ProductType(
        code=row.code,
        name=row.name,
        monthly_spread=Decimal(row.monthly_spread),
        settlement_currency_code=row.settlement_currency_code,
    )


# ------------------------------------------------------------- ExchangeRate
def to_exchange_rate(row: ExchangeRateORM) -> ExchangeRate:
    return ExchangeRate(
        base_currency=row.base_currency,
        quote_currency=row.quote_currency,
        rate=Decimal(row.rate),
        valid_from=_utc(row.valid_from),
        valid_to=_utc(row.valid_to) if row.valid_to is not None else None,
    )


# --------------------------------------------------------------- Receivable
def to_receivable(row: ReceivableORM, assignor_document: str) -> Receivable:
    return Receivable(
        id=row.id,
        assignor_document=assignor_document,
        product_code=row.product_code,
        face_value=Money(Decimal(row.face_value_amount), row.face_value_currency),
        issue_date=row.issue_date,
        due_date=row.due_date,
        external_reference=row.external_reference,
        status=ReceivableStatus(row.status),
        version=row.version,
    )


# --------------------------------------------------------------- Settlement
def to_settlement(row: SettlementORM) -> Settlement:
    return Settlement(
        id=row.id,
        receivable_id=row.receivable_id,
        discounted_value=Money(Decimal(row.discounted_amount), row.settlement_currency),
        settlement_currency=row.settlement_currency,
        settled_at=_utc(row.settled_at),
        base_rate_monthly=Decimal(row.base_rate_monthly),
        spread_monthly=Decimal(row.spread_monthly),
        term_months=Decimal(row.term_months),
        fx_rate_applied=Decimal(row.fx_rate_applied) if row.fx_rate_applied is not None else None,
        version=row.version,
        events=[to_settlement_event(e) for e in row.events],
    )


def to_settlement_event(row: SettlementEventORM) -> SettlementEvent:
    return SettlementEvent(
        id=row.id,
        event_type=SettlementEventType(row.event_type),
        occurred_at=_utc(row.occurred_at),
        actor=row.actor,
        payload=dict(row.payload) if row.payload else {},
    )
