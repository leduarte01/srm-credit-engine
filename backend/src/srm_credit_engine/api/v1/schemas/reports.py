"""Response schemas for the analytical reports surface."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReportPeriodSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start: datetime
    end: datetime


class VolumeByAssignorRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignor_id: UUID
    assignor_document: str
    assignor_legal_name: str
    receivable_count: int = Field(..., ge=0)
    total_face_value: Decimal
    total_present_value: Decimal


class VolumeByAssignorReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: ReportPeriodSchema
    rows: list[VolumeByAssignorRowSchema]


class PnlByProductRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_code: str
    product_name: str
    settlement_currency: str = Field(..., min_length=3, max_length=3)
    settlement_count: int = Field(..., ge=0)
    total_face_value_in_settlement_currency: Decimal
    total_advanced: Decimal
    total_revenue: Decimal


class PnlByProductReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: ReportPeriodSchema
    rows: list[PnlByProductRowSchema]


class AgingBucketRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bucket: str
    receivable_count: int = Field(..., ge=0)
    total_face_value: Decimal


class AgingBucketsReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference_date: datetime
    rows: list[AgingBucketRowSchema]


class FxExposureRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    currency: str = Field(..., min_length=3, max_length=3)
    receivable_count: int = Field(..., ge=0)
    total_face_value: Decimal


class FxExposureReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference_date: datetime
    rows: list[FxExposureRowSchema]
