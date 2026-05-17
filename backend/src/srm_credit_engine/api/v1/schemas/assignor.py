"""Schemas for the Assignor resource."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssignorCreate(BaseModel):
    document: str = Field(..., min_length=11, max_length=18, description="CNPJ (14 digits).")
    legal_name: str = Field(..., min_length=2, max_length=256)


class AssignorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document: str
    legal_name: str
