"""Unit tests for the resilience layer — retries, circuit breaker, wrapper."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import OperationalError

from srm_credit_engine.domain.exceptions import ExchangeRateNotFoundError
from srm_credit_engine.domain.value_objects.money import Money
from srm_credit_engine.resilience import ResilientCurrencyConverter
from srm_credit_engine.resilience.circuit_breaker import reset_breaker_factory
from srm_credit_engine.resilience.retries import retry_transient


@pytest.fixture(autouse=True)
def _reset_breakers() -> None:
    reset_breaker_factory()


class _FakeConverter:
    """Programmable stub that fails N times then succeeds."""

    def __init__(self, *, failures: int, exc: BaseException | None = None) -> None:
        self.remaining_failures = failures
        self.calls = 0
        self._exc = exc or OperationalError("simulated", None, Exception())

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        self.calls += 1
        if self.remaining_failures > 0:
            self.remaining_failures -= 1
            raise self._exc
        return Money(amount.amount * Decimal("5"), target_currency)


# ----------------------------------------------------------------- retries


@pytest.mark.asyncio
async def test_retry_transient_recovers_after_two_failures() -> None:
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise OperationalError("blip", None, Exception())
        return "ok"

    assert await retry_transient(flaky, attempts=5, wait_min=0.001, wait_max=0.01) == "ok"
    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_retry_transient_propagates_after_budget_exhausted() -> None:
    async def always_fails() -> str:
        raise OperationalError("permanent", None, Exception())

    with pytest.raises(OperationalError):
        await retry_transient(always_fails, attempts=2, wait_min=0.001, wait_max=0.01)


@pytest.mark.asyncio
async def test_retry_transient_does_not_retry_domain_errors() -> None:
    calls = {"n": 0}

    async def domain_failure() -> str:
        calls["n"] += 1
        raise ExchangeRateNotFoundError("no rate")

    with pytest.raises(ExchangeRateNotFoundError):
        await retry_transient(domain_failure, attempts=5, wait_min=0.001, wait_max=0.01)
    assert calls["n"] == 1


# ----------------------------------------------------------- resilient wrapper


@pytest.mark.asyncio
async def test_resilient_converter_recovers_from_transient_failure() -> None:
    inner = _FakeConverter(failures=2)
    wrapper = ResilientCurrencyConverter(inner, attempts=5)
    result = await wrapper.convert(
        Money(Decimal("10"), "USD"), "BRL", datetime(2024, 1, 1, tzinfo=UTC)
    )
    assert result.currency == "BRL"
    assert result.amount == Decimal("50")
    assert inner.calls == 3


@pytest.mark.asyncio
async def test_resilient_converter_propagates_domain_error_without_retry() -> None:
    inner = _FakeConverter(failures=10, exc=ExchangeRateNotFoundError("no rate"))
    wrapper = ResilientCurrencyConverter(inner, attempts=5)
    with pytest.raises(ExchangeRateNotFoundError):
        await wrapper.convert(
            Money(Decimal("10"), "USD"), "BRL", datetime(2024, 1, 1, tzinfo=UTC)
        )
    assert inner.calls == 1


@pytest.mark.asyncio
async def test_resilient_converter_opens_circuit_after_threshold() -> None:
    inner = _FakeConverter(failures=100)
    wrapper = ResilientCurrencyConverter(inner, threshold=2, ttl_seconds=10.0, attempts=1)

    # First two calls exhaust the retry budget and tick the breaker.
    for _ in range(2):
        with pytest.raises(OperationalError):
            await wrapper.convert(
                Money(Decimal("10"), "USD"),
                "BRL",
                datetime(2024, 1, 1, tzinfo=UTC),
            )

    calls_before_open = inner.calls
    # Third call must short-circuit *without* touching the inner converter.
    with pytest.raises(Exception):  # noqa: B017 — breaker raises OpenedState
        await wrapper.convert(
            Money(Decimal("10"), "USD"), "BRL", datetime(2024, 1, 1, tzinfo=UTC)
        )
    assert inner.calls == calls_before_open


@pytest.mark.asyncio
async def test_resilient_converter_uses_per_pair_breakers() -> None:
    inner_usd = _FakeConverter(failures=100)
    inner_eur = _FakeConverter(failures=0)
    wrapper_usd = ResilientCurrencyConverter(
        inner_usd, threshold=1, ttl_seconds=10.0, attempts=1
    )
    wrapper_eur = ResilientCurrencyConverter(
        inner_eur, threshold=1, ttl_seconds=10.0, attempts=1
    )

    with pytest.raises(OperationalError):
        await wrapper_usd.convert(
            Money(Decimal("10"), "USD"), "BRL", datetime(2024, 1, 1, tzinfo=UTC)
        )
    # A different currency pair carries its own breaker and must succeed.
    result = await wrapper_eur.convert(
        Money(Decimal("10"), "EUR"), "BRL", datetime(2024, 1, 1, tzinfo=UTC)
    )
    assert result.currency == "BRL"
