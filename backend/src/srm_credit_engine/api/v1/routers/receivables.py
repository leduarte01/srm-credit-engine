"""Receivable endpoints — create, lookup, filter and cancel."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query, status

from srm_credit_engine.api.v1.deps import AssignorRepoDep, ReceivableRepoDep
from srm_credit_engine.api.v1.schemas.common import ErrorResponse, PageMeta, PageResponse
from srm_credit_engine.api.v1.schemas.receivable import ReceivableCreate, ReceivableResponse
from srm_credit_engine.domain.entities.receivable import Receivable, ReceivableStatus
from srm_credit_engine.domain.exceptions import (
    AssignorNotFoundError,
    ReceivableNotFoundError,
)
from srm_credit_engine.domain.ports.repositories import ReceivableFilter
from srm_credit_engine.domain.value_objects.money import Money

router = APIRouter(prefix="/receivables", tags=["receivables"])


@router.post(
    "",
    response_model=ReceivableResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Register a new receivable for an assignor.",
)
async def create_receivable(
    payload: ReceivableCreate,
    assignors: AssignorRepoDep,
    receivables: ReceivableRepoDep,
) -> ReceivableResponse:
    document = "".join(c for c in payload.assignor_document if c.isdigit())
    assignor_id = await assignors.get_id_by_document(document)
    if assignor_id is None:
        raise AssignorNotFoundError(f"Assignor with document {document} not found.")
    receivable = Receivable(
        assignor_document=document,
        product_code=payload.product_code,
        face_value=Money(payload.face_value.amount, payload.face_value.currency.upper()),
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        external_reference=payload.external_reference,
    )
    await receivables.add(receivable, assignor_id)
    return ReceivableResponse.model_validate(receivable)


@router.get(
    "/{receivable_id}",
    response_model=ReceivableResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Lookup a receivable by id.",
)
async def get_receivable(receivable_id: UUID, repo: ReceivableRepoDep) -> ReceivableResponse:
    receivable = await repo.get_by_id(receivable_id)
    if receivable is None:
        raise ReceivableNotFoundError(f"Receivable {receivable_id} not found.")
    return ReceivableResponse.model_validate(receivable)


@router.get(
    "",
    response_model=PageResponse[ReceivableResponse],
    summary="List receivables with composable filters.",
)
async def list_receivables(
    repo: ReceivableRepoDep,
    assignor_document: str | None = Query(default=None),
    product_code: str | None = Query(default=None),
    receivable_status: ReceivableStatus | None = Query(default=None, alias="status"),  # noqa: B008
    currency: str | None = Query(default=None, min_length=3, max_length=3),
    due_from: date | None = Query(default=None),  # noqa: B008
    due_to: date | None = Query(default=None),  # noqa: B008
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> PageResponse[ReceivableResponse]:
    filters = ReceivableFilter(
        assignor_document=(
            "".join(c for c in assignor_document if c.isdigit()) if assignor_document else None
        ),
        product_code=product_code,
        status=receivable_status,
        currency=currency.upper() if currency else None,
        due_from=due_from,
        due_to=due_to,
    )
    page = await repo.list(filters, offset=offset, limit=limit)
    return PageResponse[ReceivableResponse](
        items=[ReceivableResponse.model_validate(r) for r in page.items],
        meta=PageMeta(total=page.total, offset=page.offset, limit=page.limit),
    )


@router.patch(
    "/{receivable_id}/cancel",
    response_model=ReceivableResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Cancel a receivable (must not be settled).",
)
async def cancel_receivable(receivable_id: UUID, repo: ReceivableRepoDep) -> ReceivableResponse:
    receivable = await repo.get_by_id(receivable_id)
    if receivable is None:
        raise ReceivableNotFoundError(f"Receivable {receivable_id} not found.")
    receivable.cancel()
    await repo.update(receivable)
    return ReceivableResponse.model_validate(receivable)
