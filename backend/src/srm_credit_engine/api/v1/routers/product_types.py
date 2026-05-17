"""Product type endpoints — catalog of pricing products."""

from __future__ import annotations

from fastapi import APIRouter

from srm_credit_engine.api.v1.deps import ProductTypeRepoDep
from srm_credit_engine.api.v1.schemas.common import ErrorResponse
from srm_credit_engine.api.v1.schemas.product_type import ProductTypeResponse
from srm_credit_engine.domain.exceptions import ProductTypeNotFoundError

router = APIRouter(prefix="/product-types", tags=["product-types"])


@router.get("", response_model=list[ProductTypeResponse], summary="List product types.")
async def list_product_types(repo: ProductTypeRepoDep) -> list[ProductTypeResponse]:
    products = await repo.list_all()
    return [ProductTypeResponse.model_validate(p) for p in products]


@router.get(
    "/{code}",
    response_model=ProductTypeResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get product type by code.",
)
async def get_product_type(code: str, repo: ProductTypeRepoDep) -> ProductTypeResponse:
    product = await repo.get_by_code(code)
    if product is None:
        raise ProductTypeNotFoundError(f"Product type {code} not found.")
    return ProductTypeResponse.model_validate(product)
