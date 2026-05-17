"""Assignor (cedente) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from srm_credit_engine.api.v1.deps import AssignorRepoDep
from srm_credit_engine.api.v1.schemas.assignor import AssignorCreate, AssignorResponse
from srm_credit_engine.api.v1.schemas.common import ErrorResponse, PageMeta, PageResponse
from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.exceptions import (
    AssignorNotFoundError,
    ConcurrencyConflictError,
)

router = APIRouter(prefix="/assignors", tags=["assignors"])


@router.post(
    "",
    response_model=AssignorResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Create an assignor (cedente).",
)
async def create_assignor(payload: AssignorCreate, repo: AssignorRepoDep) -> AssignorResponse:
    assignor = Assignor(document=payload.document, legal_name=payload.legal_name)
    existing = await repo.get_by_document(assignor.document)
    if existing is not None:
        raise ConcurrencyConflictError(
            f"Assignor with document {assignor.document} already exists."
        )
    await repo.add(assignor)
    return AssignorResponse.model_validate(assignor)


@router.get(
    "/by-document/{document}",
    response_model=AssignorResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Lookup assignor by document.",
)
async def get_by_document(document: str, repo: AssignorRepoDep) -> AssignorResponse:
    assignor = await repo.get_by_document("".join(c for c in document if c.isdigit()))
    if assignor is None:
        raise AssignorNotFoundError(f"Assignor with document {document} not found.")
    return AssignorResponse.model_validate(assignor)


@router.get(
    "",
    response_model=PageResponse[AssignorResponse],
    summary="List assignors with pagination.",
)
async def list_assignors(
    repo: AssignorRepoDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> PageResponse[AssignorResponse]:
    page = await repo.list(offset=offset, limit=limit)
    return PageResponse[AssignorResponse](
        items=[AssignorResponse.model_validate(a) for a in page.items],
        meta=PageMeta(total=page.total, offset=page.offset, limit=page.limit),
    )
