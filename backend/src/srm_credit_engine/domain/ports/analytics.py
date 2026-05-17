"""Analytics repository port — raw SQL backed reporting surface."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from srm_credit_engine.domain.analytics import (
    AgingBucketsReport,
    FxExposureReport,
    PnlByProductReport,
    ReportPeriod,
    VolumeByAssignorReport,
)


@runtime_checkable
class AnalyticsRepository(Protocol):
    """Read-only analytical queries executed as raw SQL."""

    async def volume_by_assignor(
        self, period: ReportPeriod, limit: int = 20
    ) -> VolumeByAssignorReport: ...

    async def pnl_by_product(self, period: ReportPeriod) -> PnlByProductReport: ...

    async def aging_buckets(self, reference_date: datetime) -> AgingBucketsReport: ...

    async def fx_exposure(self, reference_date: datetime) -> FxExposureReport: ...
