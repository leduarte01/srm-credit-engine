"""Analytical reporting domain — DTOs, ports and SQL bound to raw queries."""

from __future__ import annotations

from srm_credit_engine.domain.analytics.dtos import (
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

__all__ = [
    "AgingBucketRow",
    "AgingBucketsReport",
    "FxExposureReport",
    "FxExposureRow",
    "PnlByProductReport",
    "PnlByProductRow",
    "ReportPeriod",
    "VolumeByAssignorReport",
    "VolumeByAssignorRow",
]
