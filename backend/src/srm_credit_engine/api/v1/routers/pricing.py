"""Pricing simulation endpoint — pure, no persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter

from srm_credit_engine.api.v1.deps import ExchangeRateRepoDep, ProductTypeRepoDep, SettingsDep
from srm_credit_engine.api.v1.schemas.common import ErrorResponse, MoneySchema
from srm_credit_engine.api.v1.schemas.pricing import (
    PricingSimulateRequest,
    PricingSimulateResponse,
)
from srm_credit_engine.domain.entities.receivable import Receivable
from srm_credit_engine.domain.exceptions import ProductTypeNotFoundError
from srm_credit_engine.domain.pricing.resolver import PricingStrategyResolver
from srm_credit_engine.domain.services.pricing_service import PricingService
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.infrastructure.database_currency_converter import (
    DatabaseCurrencyConverter,
)
from srm_credit_engine.infrastructure.fallback_currency_converter import (
    FallbackCurrencyConverter,
)
from srm_credit_engine.infrastructure.live_rate_converter import LiveRateCurrencyConverter
from srm_credit_engine.observability.metrics import PRICING_OPERATIONS
from srm_credit_engine.resilience import ResilientCurrencyConverter

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post(
    "/simulate",
    response_model=PricingSimulateResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Simulate the discounted value of a hypothetical receivable.",
)
async def simulate(
    payload: PricingSimulateRequest,
    products: ProductTypeRepoDep,
    rates: ExchangeRateRepoDep,
    settings: SettingsDep,
) -> PricingSimulateResponse:
    product = await products.get_by_code(payload.product_code)
    if product is None:
        raise ProductTypeNotFoundError(f"Product type {payload.product_code} not found.")

    # Build converter based on user preference.
    # Both paths use FallbackCurrencyConverter so a transient live-API failure
    # (e.g. HTTP 429 on the free tier) never surfaces as an error to the user.
    live = LiveRateCurrencyConverter()
    if payload.use_live_rate:
        # Prefer live rate; fall back to DB when the external API is unavailable.
        fallback = FallbackCurrencyConverter(
            primary=live,
            secondary=DatabaseCurrencyConverter(rates),
            primary_label="live",
            secondary_label="database",
        )
    else:
        # Prefer DB rate; fall back to live when pair is missing from DB.
        fallback = FallbackCurrencyConverter(
            primary=DatabaseCurrencyConverter(rates),
            secondary=live,
            primary_label="database",
            secondary_label="live",
        )
    converter = ResilientCurrencyConverter(fallback)

    pricing = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=converter,
        base_rate_monthly=settings.base_rate_monthly,
    )

    # Build a transient receivable just for the calculation.
    receivable = Receivable(
        id=uuid4(),
        assignor_document="0" * 14,
        product_code=payload.product_code,
        face_value=Money(payload.face_value.amount, payload.face_value.currency.upper()),
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        external_reference=f"SIM-{uuid4().hex[:8]}",
    )

    reference_date = payload.reference_date or receivable.issue_date
    moment = datetime.now(UTC)
    try:
        priced = await pricing.price(receivable, product, reference_date, moment)
    except Exception:
        PRICING_OPERATIONS.labels(product.code, "failure").inc()
        raise
    PRICING_OPERATIONS.labels(product.code, "success").inc()

    # Determine which source provided the FX rate.
    if priced.fx_rate_applied is None:
        fx_source = None
    else:
        fx_source = fallback.last_source

    return PricingSimulateResponse(
        product_code=product.code,
        present_value=MoneySchema.model_validate(priced.pricing.present_value),
        settlement_value=MoneySchema.model_validate(priced.settlement_value),
        base_rate_monthly=priced.pricing.base_rate_monthly,
        spread_monthly=priced.pricing.spread_monthly,
        effective_monthly_rate=priced.pricing.effective_monthly_rate,
        term_months=priced.pricing.term_months,
        fx_rate_applied=priced.fx_rate_applied,
        fx_rate_source=fx_source,
    )
