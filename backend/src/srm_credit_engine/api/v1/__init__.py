"""API v1 — versioned REST surface for the credit engine."""

from __future__ import annotations

from fastapi import APIRouter

from srm_credit_engine.api.v1.routers import (
    assignors,
    exchange_rates,
    pricing,
    product_types,
    receivables,
    settlements,
)

router = APIRouter(prefix="/v1")
router.include_router(assignors.router)
router.include_router(product_types.router)
router.include_router(exchange_rates.router)
router.include_router(receivables.router)
router.include_router(settlements.router)
router.include_router(pricing.router)

__all__ = ["router"]
