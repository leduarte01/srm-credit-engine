"""Analytical reports — read-only endpoints backed by raw SQL."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query

from srm_credit_engine.api.v1.deps import AnalyticsRepoDep
from srm_credit_engine.api.v1.schemas.reports import (
    AgingBucketsReportSchema,
    FxExposureReportSchema,
    PnlByProductReportSchema,
    VolumeByAssignorReportSchema,
)
from srm_credit_engine.domain.analytics import ReportPeriod

router = APIRouter(prefix="/reports", tags=["reports"])


def _period(start: datetime, end: datetime) -> ReportPeriod:
    return ReportPeriod(start=start, end=end)


@router.get(
    "/volume-by-assignor",
    response_model=VolumeByAssignorReportSchema,
    summary="Top assignors by settled present value within a period",
)
async def volume_by_assignor(
    repo: AnalyticsRepoDep,
    period_start: Annotated[datetime, Query(description="Inclusive period start (UTC).")],
    period_end: Annotated[datetime, Query(description="Exclusive period end (UTC).")],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> VolumeByAssignorReportSchema:
    report = await repo.volume_by_assignor(_period(period_start, period_end), limit=limit)
    return VolumeByAssignorReportSchema.model_validate(report)


@router.get(
    "/pnl-by-product",
    response_model=PnlByProductReportSchema,
    summary="Revenue and advanced principal grouped by product",
)
async def pnl_by_product(
    repo: AnalyticsRepoDep,
    period_start: Annotated[datetime, Query(description="Inclusive period start (UTC).")],
    period_end: Annotated[datetime, Query(description="Exclusive period end (UTC).")],
) -> PnlByProductReportSchema:
    report = await repo.pnl_by_product(_period(period_start, period_end))
    return PnlByProductReportSchema.model_validate(report)


@router.get(
    "/aging-buckets",
    response_model=AgingBucketsReportSchema,
    summary="Outstanding receivables bucketed by days until due",
)
async def aging_buckets(
    repo: AnalyticsRepoDep,
    reference_date: Annotated[
        datetime | None,
        Query(description="Reference date (UTC). Defaults to now."),
    ] = None,
) -> AgingBucketsReportSchema:
    ref = reference_date or datetime.now(UTC)
    report = await repo.aging_buckets(ref)
    return AgingBucketsReportSchema.model_validate(report)


@router.get(
    "/fx-exposure",
    response_model=FxExposureReportSchema,
    summary="Outstanding face value grouped by face-value currency",
)
async def fx_exposure(
    repo: AnalyticsRepoDep,
    reference_date: Annotated[
        datetime | None,
        Query(description="Reference date (UTC). Defaults to now."),
    ] = None,
) -> FxExposureReportSchema:
    ref = reference_date or datetime.now(UTC)
    report = await repo.fx_exposure(ref)
    return FxExposureReportSchema.model_validate(report)
