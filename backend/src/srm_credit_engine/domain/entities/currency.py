"""Currency reference entity (ISO-4217)."""

from __future__ import annotations

from dataclasses import dataclass

ISO_4217_CODE_LENGTH = 3


@dataclass(frozen=True, slots=True)
class Currency:
    """ISO-4217 currency reference (e.g. BRL, USD)."""

    code: str
    name: str
    decimal_places: int = 2

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or len(self.code) != ISO_4217_CODE_LENGTH:
            raise ValueError("Currency.code must be a 3-letter ISO-4217 code.")
        if self.decimal_places < 0:
            raise ValueError("decimal_places must be non-negative.")
        object.__setattr__(self, "code", self.code.upper())
