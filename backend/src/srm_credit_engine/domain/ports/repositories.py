"""Repository ports (Protocols) for the domain to consume."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

from srm_credit_engine.domain.entities.assignor import Assignor
from srm_credit_engine.domain.entities.exchange_rate import ExchangeRate
from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable, ReceivableStatus
from srm_credit_engine.domain.entities.settlement import Settlement


@dataclass(frozen=True, slots=True)
class ReceivableFilter:
    """Server-side filters for receivable listings."""

    assignor_document: str | None = None
    product_code: str | None = None
    status: ReceivableStatus | None = None
    currency: str | None = None
    due_from: date | None = None
    due_to: date | None = None


@dataclass(frozen=True, slots=True)
class Page[T]:
    """Paginated result envelope."""

    items: list[T]
    total: int
    offset: int
    limit: int


@runtime_checkable
class AssignorRepository(Protocol):
    async def get_by_id(self, assignor_id: UUID) -> Assignor | None: ...
    async def get_by_document(self, document: str) -> Assignor | None: ...
    async def get_id_by_document(self, document: str) -> UUID | None: ...
    async def add(self, assignor: Assignor) -> UUID: ...
    async def list(self, offset: int = 0, limit: int = 50) -> Page[Assignor]: ...


@runtime_checkable
class ProductTypeRepository(Protocol):
    async def get_by_code(self, code: str) -> ProductType | None: ...
    async def list_all(self) -> list[ProductType]: ...


@runtime_checkable
class ExchangeRateRepository(Protocol):
    async def get_active(
        self, base_currency: str, quote_currency: str, at: datetime
    ) -> ExchangeRate | None: ...
    async def add(self, rate: ExchangeRate) -> UUID: ...
    async def list_history(self, base_currency: str, quote_currency: str) -> list[ExchangeRate]: ...


@runtime_checkable
class ReceivableRepository(Protocol):
    async def get_by_id(self, receivable_id: UUID) -> Receivable | None: ...
    async def add(self, receivable: Receivable, assignor_id: UUID) -> UUID: ...
    async def update(self, receivable: Receivable) -> None: ...
    async def list(
        self,
        filters: ReceivableFilter,
        offset: int = 0,
        limit: int = 50,
    ) -> Page[Receivable]: ...


@runtime_checkable
class SettlementRepository(Protocol):
    async def add(self, settlement: Settlement) -> UUID: ...
    async def get_by_id(self, settlement_id: UUID) -> Settlement | None: ...
