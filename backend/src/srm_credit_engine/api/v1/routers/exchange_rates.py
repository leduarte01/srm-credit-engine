"""Exchange rate endpoints — upsert and time-based lookup."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Query, status

from srm_credit_engine.api.v1.deps import ExchangeRateRepoDep
from srm_credit_engine.api.v1.schemas.common import ErrorResponse
from srm_credit_engine.api.v1.schemas.exchange_rate import (
    ExchangeRateCreate,
    ExchangeRateResponse,
)
from srm_credit_engine.domain.entities.exchange_rate import ExchangeRate
from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError

router = APIRouter(prefix="/fx-rates", tags=["fx-rates"])


@router.post(
    "",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Register a new FX rate (immutable history).",
)
async def create_fx_rate(
    payload: ExchangeRateCreate, repo: ExchangeRateRepoDep
) -> ExchangeRateResponse:
    rate = ExchangeRate(
        base_currency=payload.base_currency.upper(),
        quote_currency=payload.quote_currency.upper(),
        rate=payload.rate,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
    )
    await repo.add(rate)
    return ExchangeRateResponse.model_validate(rate)


@router.get(
    "/{base_currency}/{quote_currency}",
    response_model=ExchangeRateResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get the FX rate active at a given moment (default: now).",
)
async def get_active_rate(
    base_currency: str,
    quote_currency: str,
    repo: ExchangeRateRepoDep,
    at: datetime | None = Query(default=None, description="Moment in time (UTC). Defaults to now."),  # noqa: B008
) -> ExchangeRateResponse:
    moment = at or datetime.now(UTC)
    rate = await repo.get_active(base_currency.upper(), quote_currency.upper(), moment)
    if rate is None:
        raise ExchangeRateNotFoundError(
            f"No FX rate {base_currency}->{quote_currency} active at {moment.isoformat()}."
        )
    return ExchangeRateResponse.model_validate(rate)


@router.get(
    "/{base_currency}/{quote_currency}/history",
    response_model=list[ExchangeRateResponse],
    summary="List the full FX rate history for a currency pair.",
)
async def list_history(
    base_currency: str, quote_currency: str, repo: ExchangeRateRepoDep
) -> list[ExchangeRateResponse]:
    history = await repo.list_history(base_currency.upper(), quote_currency.upper())
    return [ExchangeRateResponse.model_validate(r) for r in history]
