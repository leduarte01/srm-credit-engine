"""Immutable DTOs returned by the analytics queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ReportPeriod:
    """Half-open period ``[start, end)`` shared by time-bounded reports."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("ReportPeriod.end must be strictly greater than start")


@dataclass(frozen=True, slots=True)
class VolumeByAssignorRow:
    assignor_id: UUID
    assignor_document: str
    assignor_legal_name: str
    receivable_count: int
    total_face_value: Decimal
    total_present_value: Decimal


@dataclass(frozen=True, slots=True)
class VolumeByAssignorReport:
    period: ReportPeriod
    rows: tuple[VolumeByAssignorRow, ...]


@dataclass(frozen=True, slots=True)
class PnlByProductRow:
    product_code: str
    product_name: str
    settlement_count: int
    total_face_value_in_settlement_currency: Decimal
    total_advanced: Decimal
    total_revenue: Decimal
    settlement_currency: str


@dataclass(frozen=True, slots=True)
class PnlByProductReport:
    period: ReportPeriod
    rows: tuple[PnlByProductRow, ...]


@dataclass(frozen=True, slots=True)
class AgingBucketRow:
    bucket: str
    receivable_count: int
    total_face_value: Decimal


@dataclass(frozen=True, slots=True)
class AgingBucketsReport:
    reference_date: datetime
    rows: tuple[AgingBucketRow, ...]


@dataclass(frozen=True, slots=True)
class FxExposureRow:
    currency: str
    receivable_count: int
    total_face_value: Decimal


@dataclass(frozen=True, slots=True)
class FxExposureReport:
    reference_date: datetime
    rows: tuple[FxExposureRow, ...]
