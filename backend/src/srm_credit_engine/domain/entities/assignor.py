"""Assignor (cedente) entity — the originator of the receivable."""

from __future__ import annotations

from dataclasses import dataclass

CNPJ_DIGITS = 14


@dataclass(frozen=True, slots=True)
class Assignor:
    """Legal entity that assigns receivables to the fund."""

    document: str
    legal_name: str

    def __post_init__(self) -> None:
        digits = "".join(c for c in self.document if c.isdigit())
        if len(digits) != CNPJ_DIGITS:
            raise ValueError("Assignor.document must contain 14 digits (CNPJ).")
        if not self.legal_name or not self.legal_name.strip():
            raise ValueError("Assignor.legal_name is required.")
        object.__setattr__(self, "document", digits)
