"""Concrete :class:`AnalyticsRepository` backed by raw SQL over AsyncSession.

In production the underlying driver is asyncpg (PostgreSQL); in the test suite
the same SQL runs against aiosqlite. All statements are parametrized and use
only constructs that both dialects understand.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from srm_credit_engine.domain.analytics import (
    AgingBucketRow,
    AgingBucketsReport,
    FxExposureReport,
    FxExposureRow,
    PnlByProductReport,
    PnlByProductRow,
    ReportPeriod,
    VolumeByAssignorReport,
    VolumeByAssignorRow,
)
from srm_credit_engine.domain.analytics.queries import (
    SQL_AGING_BUCKETS,
    SQL_FX_EXPOSURE,
    SQL_PNL_BY_PRODUCT,
    SQL_VOLUME_BY_ASSIGNOR,
)


def _to_decimal(value: object) -> Decimal:
    """Coerce driver-native numeric to ``Decimal`` without float drift."""
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _to_uuid(value: object) -> UUID:
    """Coerce driver-native UUID representation to :class:`uuid.UUID`."""
    if isinstance(value, UUID):
        return value
    if isinstance(value, bytes):
        return UUID(bytes=value)
    return UUID(str(value))


class SqlAnalyticsRepository:
    """Raw-SQL backed implementation of :class:`AnalyticsRepository`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def volume_by_assignor(
        self, period: ReportPeriod, limit: int = 20
    ) -> VolumeByAssignorReport:
        result = await self._session.execute(
            text(SQL_VOLUME_BY_ASSIGNOR),
            {
                "period_start": period.start,
                "period_end": period.end,
                "row_limit": limit,
            },
        )
        rows = tuple(
            VolumeByAssignorRow(
                assignor_id=_to_uuid(row.assignor_id),
                assignor_document=str(row.assignor_document),
                assignor_legal_name=str(row.assignor_legal_name),
                receivable_count=int(row.receivable_count),
                total_face_value=_to_decimal(row.total_face_value),
                total_present_value=_to_decimal(row.total_present_value),
            )
            for row in result.mappings()
        )
        return VolumeByAssignorReport(period=period, rows=rows)

    async def pnl_by_product(self, period: ReportPeriod) -> PnlByProductReport:
        result = await self._session.execute(
            text(SQL_PNL_BY_PRODUCT),
            {"period_start": period.start, "period_end": period.end},
        )
        rows = tuple(
            PnlByProductRow(
                product_code=str(row.product_code),
                product_name=str(row.product_name),
                settlement_currency=str(row.settlement_currency),
                settlement_count=int(row.settlement_count),
                total_face_value_in_settlement_currency=_to_decimal(
                    row.total_face_value_in_settlement_currency
                ),
                total_advanced=_to_decimal(row.total_advanced),
                total_revenue=_to_decimal(row.total_revenue),
            )
            for row in result.mappings()
        )
        return PnlByProductReport(period=period, rows=rows)

    async def aging_buckets(self, reference_date: datetime) -> AgingBucketsReport:
        ref = reference_date.date()
        result = await self._session.execute(
            text(SQL_AGING_BUCKETS),
            {
                "ref_date": ref,
                "d30": ref + timedelta(days=30),
                "d60": ref + timedelta(days=60),
                "d90": ref + timedelta(days=90),
            },
        )
        rows = tuple(
            AgingBucketRow(
                bucket=str(row.bucket),
                receivable_count=int(row.receivable_count),
                total_face_value=_to_decimal(row.total_face_value),
            )
            for row in result.mappings()
        )
        return AgingBucketsReport(reference_date=reference_date, rows=rows)

    async def fx_exposure(self, reference_date: datetime) -> FxExposureReport:
        result = await self._session.execute(text(SQL_FX_EXPOSURE))
        rows = tuple(
            FxExposureRow(
                currency=str(row.currency),
                receivable_count=int(row.receivable_count),
                total_face_value=_to_decimal(row.total_face_value),
            )
            for row in result.mappings()
        )
        return FxExposureReport(reference_date=reference_date, rows=rows)
