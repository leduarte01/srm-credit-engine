"""Shared schemas used across multiple v1 resources."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MoneySchema(BaseModel):
    """ISO-4217 monetary amount represented as a decimal string for precision."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"amount": "10000.00", "currency": "BRL"}},
    )

    amount: Decimal = Field(..., gt=0, description="Positive decimal amount.")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO-4217 code.")


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all failing endpoints."""

    code: str = Field(..., description="Stable machine-readable error code.")
    message: str = Field(..., description="Human-readable message.")
    details: list[dict[str, Any]] | None = Field(
        default=None, description="Optional per-field validation details."
    )


class PageMeta(BaseModel):
    """Pagination metadata accompanying every list response."""

    total: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=200)


class PageResponse[T](BaseModel):
    """Generic paginated envelope.

    Subclasses bind ``items`` to a concrete schema (e.g. ``list[AssignorResponse]``).
    """

    items: list[T]
    meta: PageMeta
