"""Domain exceptions — translated to HTTP problem details by the API layer."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain (business rule) violations."""

    code: str = "DOMAIN_ERROR"
    http_status: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidReceivableError(DomainError):
    code = "RECEIVABLE_INVALID"
    http_status = 422


class PricingStrategyNotFoundError(DomainError):
    code = "STRATEGY_NOT_FOUND"
    http_status = 404


class ExchangeRateNotFoundError(DomainError):
    code = "FX_RATE_NOT_FOUND"
    http_status = 404


class ConcurrencyConflictError(DomainError):
    code = "CONCURRENCY_CONFLICT"
    http_status = 409


class AlreadySettledError(DomainError):
    code = "ALREADY_SETTLED"
    http_status = 409


class ReceivableNotFoundError(DomainError):
    code = "RECEIVABLE_NOT_FOUND"
    http_status = 404
