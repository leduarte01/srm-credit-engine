"""Seed static catalog: currencies and product types.

Revision ID: 0002_seed_catalog
Revises: 0001_initial_schema
Create Date: 2025-01-01 00:01:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_seed_catalog"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO currency (code, name, decimal_places) VALUES
                ('BRL', 'Real Brasileiro',   2),
                ('USD', 'Dólar Americano',   2),
                ('EUR', 'Euro',              2)
            ON CONFLICT (code) DO NOTHING;
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO product_type (code, name, monthly_spread, settlement_currency_code) VALUES
                ('DUPLICATA',    'Duplicata Mercantil', 0.015000, 'BRL'),
                ('CHEQUE_PRE',   'Cheque Pré-datado',   0.025000, 'BRL'),
                ('CONTRATO_USD', 'Contrato em USD',     0.012000, 'USD')
            ON CONFLICT (code) DO NOTHING;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM product_type WHERE code IN ('DUPLICATA', 'CHEQUE_PRE', 'CONTRATO_USD');"
        )
    )
    op.execute(
        sa.text("DELETE FROM currency WHERE code IN ('BRL', 'USD', 'EUR');")
    )
