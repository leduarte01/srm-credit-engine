"""Receivable aggregate root — the central asset of the credit engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from srm_credit_engine.domain.exceptions import (
    AlreadySettledError,
    InvalidReceivableError,
)
from srm_credit_engine.domain.value_objects.money import Money

DAYS_PER_MONTH = Decimal("30")


class ReceivableStatus(StrEnum):
    """Lifecycle status of a receivable."""

    PENDING = "PENDING"
    PRICED = "PRICED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class Receivable:
    """A future cash flow assigned to the fund and discounted by the engine.

    Mutable aggregate; uses ``version`` for optimistic locking when persisted.
    """

    assignor_document: str
    product_code: str
    face_value: Money
    issue_date: date
    due_date: date
    external_reference: str
    id: UUID = field(default_factory=uuid4)
    status: ReceivableStatus = ReceivableStatus.PENDING
    version: int = 1

    def __post_init__(self) -> None:
        if self.due_date <= self.issue_date:
            raise InvalidReceivableError("due_date must be after issue_date.")
        if self.face_value.amount <= 0:
            raise InvalidReceivableError("face_value must be positive.")
        if not self.external_reference or not self.external_reference.strip():
            raise InvalidReceivableError("external_reference is required.")

    def term_in_months(self, reference: date | None = None) -> Decimal:
        """Compute remaining term in months from ``reference`` (default: issue_date).

        Uses a 30-day month convention typical of Brazilian receivables markets.
        Returns a :class:`Decimal` so downstream math stays exact.
        """
        anchor = reference if reference is not None else self.issue_date
        if self.due_date <= anchor:
            return Decimal("0")
        days = Decimal((self.due_date - anchor).days)
        return days / DAYS_PER_MONTH

    def mark_as_priced(self) -> None:
        if self.status is ReceivableStatus.SETTLED:
            raise AlreadySettledError(f"Receivable {self.id} already settled.")
        if self.status is ReceivableStatus.CANCELLED:
            raise InvalidReceivableError("Cannot price a cancelled receivable.")
        self.status = ReceivableStatus.PRICED
        self.version += 1

    def mark_as_settled(self) -> None:
        if self.status is ReceivableStatus.SETTLED:
            raise AlreadySettledError(f"Receivable {self.id} already settled.")
        if self.status is ReceivableStatus.CANCELLED:
            raise InvalidReceivableError("Cannot settle a cancelled receivable.")
        self.status = ReceivableStatus.SETTLED
        self.version += 1

    def cancel(self) -> None:
        if self.status is ReceivableStatus.SETTLED:
            raise AlreadySettledError("Cannot cancel a settled receivable.")
        self.status = ReceivableStatus.CANCELLED
        self.version += 1
