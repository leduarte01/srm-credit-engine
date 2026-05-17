"""Settlement aggregate and its event-log children for the audit trail."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from srm_credit_engine.domain.value_objects.money import Money


class SettlementEventType(StrEnum):
    """Auditable lifecycle event of a settlement."""

    CREATED = "CREATED"
    PRICED = "PRICED"
    FX_APPLIED = "FX_APPLIED"
    SETTLED = "SETTLED"
    REVERSED = "REVERSED"


@dataclass(frozen=True, slots=True)
class SettlementEvent:
    """Immutable record appended to the settlement's audit log."""

    event_type: SettlementEventType
    occurred_at: datetime
    actor: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class Settlement:
    """Represents the pricing decision and cash settlement of a receivable."""

    receivable_id: UUID
    discounted_value: Money
    settlement_currency: str
    settled_at: datetime
    base_rate_monthly: Decimal
    spread_monthly: Decimal
    term_months: Decimal
    fx_rate_applied: Decimal | None = None
    id: UUID = field(default_factory=uuid4)
    version: int = 1
    events: list[SettlementEvent] = field(default_factory=list)

    def append_event(self, event: SettlementEvent) -> None:
        self.events.append(event)
        self.version += 1
