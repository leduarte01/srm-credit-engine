"""Settlement endpoints — orchestrates pricing, FX, persistence and audit log."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, status

from srm_credit_engine.api.v1.deps import (
    PricingServiceDep,
    ProductTypeRepoDep,
    ReceivableRepoDep,
    SettlementRepoDep,
)
from srm_credit_engine.api.v1.schemas.common import ErrorResponse
from srm_credit_engine.api.v1.schemas.settlement import SettlementCreate, SettlementResponse
from srm_credit_engine.domain.entities.settlement import (
    Settlement,
    SettlementEvent,
    SettlementEventType,
)
from srm_credit_engine.domain.exceptions import (
    ProductTypeNotFoundError,
    ReceivableNotFoundError,
    SettlementNotFoundError,
)
from srm_credit_engine.observability.metrics import SETTLEMENT_OPERATIONS

router = APIRouter(prefix="/settlements", tags=["settlements"])

_ACTOR = "api.v1.settlements"


@router.post(
    "",
    response_model=SettlementResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Price and settle a receivable, persisting the audit trail.",
)
async def create_settlement(
    payload: SettlementCreate,
    receivables: ReceivableRepoDep,
    products: ProductTypeRepoDep,
    settlements: SettlementRepoDep,
    pricing: PricingServiceDep,
) -> SettlementResponse:
    receivable = await receivables.get_by_id(payload.receivable_id)
    if receivable is None:
        raise ReceivableNotFoundError(f"Receivable {payload.receivable_id} not found.")

    product = await products.get_by_code(receivable.product_code)
    if product is None:
        raise ProductTypeNotFoundError(f"Product type {receivable.product_code} not found.")

    reference_date = payload.reference_date or receivable.issue_date
    moment = datetime.now(UTC)
    priced = await pricing.price(receivable, product, reference_date, moment)

    settlement = Settlement(
        receivable_id=receivable.id,
        discounted_value=priced.settlement_value,
        settlement_currency=product.settlement_currency_code,
        settled_at=moment,
        base_rate_monthly=priced.pricing.base_rate_monthly,
        spread_monthly=priced.pricing.spread_monthly,
        term_months=priced.pricing.term_months,
        fx_rate_applied=priced.fx_rate_applied,
    )
    settlement.append_event(
        SettlementEvent(
            event_type=SettlementEventType.CREATED,
            occurred_at=moment,
            actor=_ACTOR,
            payload={"receivable_id": str(receivable.id)},
        )
    )
    settlement.append_event(
        SettlementEvent(
            event_type=SettlementEventType.PRICED,
            occurred_at=moment,
            actor=_ACTOR,
            payload={
                "present_value": str(priced.pricing.present_value.amount),
                "currency": priced.pricing.present_value.currency,
                "term_months": str(priced.pricing.term_months),
            },
        )
    )
    if priced.fx_rate_applied is not None:
        settlement.append_event(
            SettlementEvent(
                event_type=SettlementEventType.FX_APPLIED,
                occurred_at=moment,
                actor=_ACTOR,
                payload={
                    "fx_rate": str(priced.fx_rate_applied),
                    "from_currency": priced.pricing.present_value.currency,
                    "to_currency": product.settlement_currency_code,
                },
            )
        )
    settlement.append_event(
        SettlementEvent(
            event_type=SettlementEventType.SETTLED,
            occurred_at=moment,
            actor=_ACTOR,
            payload={
                "discounted_amount": str(priced.settlement_value.amount),
                "currency": priced.settlement_value.currency,
            },
        )
    )

    receivable.mark_as_priced()
    await receivables.update(receivable)
    receivable.mark_as_settled()
    await receivables.update(receivable)

    await settlements.add(settlement)
    SETTLEMENT_OPERATIONS.labels(product.code, "success").inc()
    return _to_response(settlement)


@router.get(
    "/{settlement_id}",
    response_model=SettlementResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Lookup a settlement by id.",
)
async def get_settlement(
    settlement_id: UUID, repo: SettlementRepoDep
) -> SettlementResponse:
    settlement = await repo.get_by_id(settlement_id)
    if settlement is None:
        raise SettlementNotFoundError(f"Settlement {settlement_id} not found.")
    return _to_response(settlement)


def _to_response(settlement: Settlement) -> SettlementResponse:
    return SettlementResponse.model_validate(settlement)
