"""SQLAlchemy 2.0 declarative ORM models mapping to the credit engine schema.

Mappings mirror ``db/migrations/V1__init.sql`` and are kept portable so the
test suite can spin them up on aiosqlite while production runs on PostgreSQL.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class CurrencyORM(Base):
    __tablename__ = "currency"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, nullable=False, default=2)


class ExchangeRateORM(Base):
    __tablename__ = "exchange_rate"
    __table_args__ = (
        CheckConstraint("base_currency <> quote_currency", name="ck_fx_distinct_currencies"),
        CheckConstraint("rate > 0", name="ck_fx_rate_positive"),
        Index("idx_fx_pair_validity", "base_currency", "quote_currency", "valid_from"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    base_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currency.code"), nullable=False
    )
    quote_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currency.code"), nullable=False
    )
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProductTypeORM(Base):
    __tablename__ = "product_type"
    __table_args__ = (CheckConstraint("monthly_spread >= 0", name="ck_product_spread_nonneg"),)

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    monthly_spread: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    settlement_currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currency.code"), nullable=False
    )


class AssignorORM(Base):
    __tablename__ = "assignor"
    __table_args__ = (UniqueConstraint("document", name="uq_assignor_document"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    document: Mapped[str] = mapped_column(String(14), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(256), nullable=False)


class ReceivableORM(Base):
    __tablename__ = "receivable"
    __table_args__ = (
        CheckConstraint("due_date > issue_date", name="ck_receivable_dates"),
        CheckConstraint("face_value_amount > 0", name="ck_receivable_face_positive"),
        UniqueConstraint(
            "assignor_id", "external_reference", name="uq_receivable_assignor_external_ref"
        ),
        Index("idx_receivable_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    assignor_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("assignor.id", ondelete="RESTRICT"), nullable=False
    )
    product_code: Mapped[str] = mapped_column(
        String(64), ForeignKey("product_type.code"), nullable=False
    )
    face_value_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    face_value_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currency.code"), nullable=False
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    external_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SettlementORM(Base):
    __tablename__ = "settlement"
    __table_args__ = (
        CheckConstraint("discounted_amount > 0", name="ck_settlement_discounted_positive"),
        Index("idx_settlement_settled_at", "settled_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    receivable_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("receivable.id", ondelete="RESTRICT"), nullable=False
    )
    discounted_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    settlement_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currency.code"), nullable=False
    )
    settled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    base_rate_monthly: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    spread_monthly: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    term_months: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    fx_rate_applied: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    events: Mapped[list[SettlementEventORM]] = relationship(
        back_populates="settlement", cascade="all, delete-orphan", lazy="selectin"
    )


class SettlementEventORM(Base):
    __tablename__ = "settlement_event"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    settlement_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("settlement.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    settlement: Mapped[SettlementORM] = relationship(back_populates="events")
