"""Baseline schema for the credit engine.

This revision is the source of truth for application-managed migrations and
mirrors ``db/migrations/V1__init.sql`` (which exists for DBA/Flyway-style
operators). Tables, constraints and seed rows match 1:1.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "currency",
        sa.Column("code", sa.String(3), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("decimal_places", sa.Integer, nullable=False, server_default="2"),
    )
    op.create_table(
        "exchange_rate",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("base_currency", sa.String(3), sa.ForeignKey("currency.code"), nullable=False),
        sa.Column("quote_currency", sa.String(3), sa.ForeignKey("currency.code"), nullable=False),
        sa.Column("rate", sa.Numeric(20, 8), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("base_currency <> quote_currency", name="ck_fx_distinct_currencies"),
        sa.CheckConstraint("rate > 0", name="ck_fx_rate_positive"),
    )
    op.create_index(
        "idx_fx_pair_validity",
        "exchange_rate",
        ["base_currency", "quote_currency", "valid_from"],
    )
    op.create_table(
        "product_type",
        sa.Column("code", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("monthly_spread", sa.Numeric(9, 6), nullable=False),
        sa.Column(
            "settlement_currency_code", sa.String(3), sa.ForeignKey("currency.code"), nullable=False
        ),
        sa.CheckConstraint("monthly_spread >= 0", name="ck_product_spread_nonneg"),
    )
    op.create_table(
        "assignor",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("document", sa.String(14), nullable=False),
        sa.Column("legal_name", sa.String(256), nullable=False),
        sa.UniqueConstraint("document", name="uq_assignor_document"),
    )
    op.create_table(
        "receivable",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column(
            "assignor_id",
            sa.Uuid,
            sa.ForeignKey("assignor.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "product_code", sa.String(64), sa.ForeignKey("product_type.code"), nullable=False
        ),
        sa.Column("face_value_amount", sa.Numeric(20, 4), nullable=False),
        sa.Column(
            "face_value_currency", sa.String(3), sa.ForeignKey("currency.code"), nullable=False
        ),
        sa.Column("issue_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("external_reference", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="PENDING"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("due_date > issue_date", name="ck_receivable_dates"),
        sa.CheckConstraint("face_value_amount > 0", name="ck_receivable_face_positive"),
        sa.UniqueConstraint(
            "assignor_id", "external_reference", name="uq_receivable_assignor_external_ref"
        ),
    )
    op.create_index("idx_receivable_status", "receivable", ["status"])
    op.create_table(
        "settlement",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column(
            "receivable_id",
            sa.Uuid,
            sa.ForeignKey("receivable.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("discounted_amount", sa.Numeric(20, 4), nullable=False),
        sa.Column(
            "settlement_currency", sa.String(3), sa.ForeignKey("currency.code"), nullable=False
        ),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("base_rate_monthly", sa.Numeric(9, 6), nullable=False),
        sa.Column("spread_monthly", sa.Numeric(9, 6), nullable=False),
        sa.Column("term_months", sa.Numeric(10, 4), nullable=False),
        sa.Column("fx_rate_applied", sa.Numeric(20, 8), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.CheckConstraint("discounted_amount > 0", name="ck_settlement_discounted_positive"),
    )
    op.create_index("idx_settlement_settled_at", "settlement", ["settled_at"])
    op.create_table(
        "settlement_event",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column(
            "settlement_id",
            sa.Uuid,
            sa.ForeignKey("settlement.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(128), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("settlement_event")
    op.drop_index("idx_settlement_settled_at", table_name="settlement")
    op.drop_table("settlement")
    op.drop_index("idx_receivable_status", table_name="receivable")
    op.drop_table("receivable")
    op.drop_table("assignor")
    op.drop_table("product_type")
    op.drop_index("idx_fx_pair_validity", table_name="exchange_rate")
    op.drop_table("exchange_rate")
    op.drop_table("currency")
