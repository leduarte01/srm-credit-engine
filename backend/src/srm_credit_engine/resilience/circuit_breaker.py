"""Process-wide circuit breaker factory backed by :mod:`purgatory`.

Domain errors (anything inheriting from :class:`DomainError`) are excluded
from the failure count: a missing FX rate or a "receivable not found"
business response must not burn the budget that protects against actual
infrastructure outages.
"""

from __future__ import annotations

from purgatory import AsyncCircuitBreakerFactory

from srm_credit_engine.domain.exceptions import DomainError

DEFAULT_THRESHOLD = 5
DEFAULT_TTL_SECONDS = 30.0


class _State:
    factory: AsyncCircuitBreakerFactory | None = None


def get_breaker_factory(
    *,
    threshold: int = DEFAULT_THRESHOLD,
    ttl: float = DEFAULT_TTL_SECONDS,
) -> AsyncCircuitBreakerFactory:
    """Return the lazily-built singleton breaker factory."""
    if _State.factory is None:
        _State.factory = AsyncCircuitBreakerFactory(
            default_threshold=threshold,
            default_ttl=ttl,
            exclude=[DomainError],
        )
    return _State.factory


def reset_breaker_factory() -> None:
    """Reset the singleton — exposed for tests that need a fresh state."""
    _State.factory = None
