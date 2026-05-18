"""Retry policies for transient failures, powered by :mod:`tenacity`.

Transient = the *infrastructure* failed in a way that can plausibly succeed
on retry (network blip, deadlock, lock timeout). Business / domain errors
must **never** be retried — they are deterministic and would only burn
budget. Concretely, the policy here retries on
:class:`sqlalchemy.exc.OperationalError`, :class:`asyncio.TimeoutError`
and :class:`ConnectionError`, and re-raises everything else immediately.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from sqlalchemy.exc import DBAPIError, OperationalError
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    OperationalError,
    DBAPIError,
    asyncio.TimeoutError,
    ConnectionError,
)

DEFAULT_ATTEMPTS = 3
DEFAULT_WAIT_MIN = 0.1
DEFAULT_WAIT_MAX = 2.0


async def retry_transient[T](
    func: Callable[[], Awaitable[T]],
    *,
    attempts: int = DEFAULT_ATTEMPTS,
    wait_min: float = DEFAULT_WAIT_MIN,
    wait_max: float = DEFAULT_WAIT_MAX,
) -> T:
    """Run ``func`` with exponential backoff + jitter on transient errors.

    Reraises the original exception once ``attempts`` is exhausted (instead
    of tenacity's :class:`RetryError`) so callers continue to handle the
    underlying error type.
    """
    retrying = AsyncRetrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=wait_min, max=wait_max) + wait_random(0, wait_min),
        retry=retry_if_exception_type(TRANSIENT_EXCEPTIONS),
        reraise=True,
    )
    try:
        async for attempt in retrying:
            with attempt:
                return await func()
    except RetryError as exc:  # pragma: no cover — reraise=True bypasses this
        raise exc.last_attempt.exception() from exc  # type: ignore[misc]
    raise RuntimeError("unreachable")  # pragma: no cover
