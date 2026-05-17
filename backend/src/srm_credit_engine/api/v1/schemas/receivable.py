"""Schemas for the Receivable resource."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from srm_credit_engine.api.v1.schemas.common import MoneySchema
from srm_credit_engine.domain.entities.receivable import ReceivableStatus


class ReceivableCreate(BaseModel):
    assignor_document: str = Field(..., min_length=11, max_length=18)
    product_code: str = Field(..., min_length=2, max_length=64)
    face_value: MoneySchema
    issue_date: date
    due_date: date
    external_reference: str = Field(..., min_length=1, max_length=64)


class ReceivableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assignor_document: str
    product_code: str
    face_value: MoneySchema
    issue_date: date
    due_date: date
    external_reference: str
    status: ReceivableStatus
    version: int
