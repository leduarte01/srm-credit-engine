# PR #11 — Resilience: retries and circuit breakers

## Summary
Adds a resilience layer that wraps infrastructure-bound operations with
**tenacity** retries on transient failures and **purgatory** circuit
breakers scoped per currency pair. The first integration point is the
FX conversion path: `ResilientCurrencyConverter` decorates
`DatabaseCurrencyConverter` and is injected wherever the pricing
service needs FX, without touching the domain layer.

## Scope
- New package `srm_credit_engine.resilience/`:
  - `retries.py` — `retry_transient(func, *, attempts, wait_min,
    wait_max)`. Exponential backoff + jitter via
    `wait_exponential + wait_random`. Retries only on the
    **transient set**: `OperationalError`, `DBAPIError`,
    `asyncio.TimeoutError`, `ConnectionError`. `reraise=True` so the
    caller still catches the original exception type, not tenacity's
    `RetryError`.
  - `circuit_breaker.py` — process-wide
    `AsyncCircuitBreakerFactory` singleton, lazily built. Configured
    with `exclude=[DomainError]` so business outcomes (missing FX
    rate, validation errors) never trip the breaker. `_State` class
    instead of `global` to keep ruff (`PLW0603`) happy.
  - `resilient_converter.py` — `ResilientCurrencyConverter`
    implements the `CurrencyConverter` port. Each call resolves a
    breaker named `fx:{base}->{quote}` so a flaky pair cannot freeze
    unrelated ones, then runs the inner call inside
    `async with breaker:` + `retry_transient(...)`.
- `api/v1/deps.py` — `get_currency_converter` now returns
  `ResilientCurrencyConverter(DatabaseCurrencyConverter(rates))`
  typed as the `CurrencyConverter` port.

## Quality gates
- **Ruff**: passed
- **Mypy --strict**: 64 source files, no issues
- **Pytest**: **148/148** passing (was 141)
- **Coverage**: **89.68%** global (gate ≥80%)

## New tests — `tests/unit/test_resilience.py`
- `retry_transient` recovers after two transient failures (3 calls,
  succeeds on the third).
- `retry_transient` exhausts the budget and reraises the **original**
  `OperationalError` (not `RetryError`).
- `retry_transient` does **not** retry domain errors
  (`ExchangeRateNotFoundError` called exactly once).
- `ResilientCurrencyConverter` recovers transparently from transient
  failures and returns the inner result.
- `ResilientCurrencyConverter` propagates domain errors without
  retrying and without tripping the breaker.
- Circuit opens after `threshold` consecutive transient failures: the
  next call short-circuits *without* touching the inner converter.
- Per-pair isolation: a tripped breaker for `USD->BRL` does not
  affect `EUR->BRL`.

## Architectural decisions
- **Where to apply resilience**: at the *adapter boundary*, not in
  the domain. The domain stays deterministic; only the
  infrastructure-coupled implementation of `CurrencyConverter`
  receives retries and breakers. Domain code is unaware.
- **Exclude `DomainError` from both policies**: business errors are
  deterministic outcomes. Retrying them wastes the budget; counting
  them against the breaker would open it during normal "no rate
  available" workloads and turn a 4xx into a 5xx.
- **Reraise originals instead of `RetryError`**: callers (the pricing
  service, FastAPI exception handlers) already understand the
  underlying exception types. Wrapping them would force a second
  layer of unwrapping.
- **Breaker per `base->quote`**: failure modes are pair-scoped (a
  missing provider for one currency does not imply outage for
  another). Sharing a global breaker would create false positives.
- **Singleton factory via `class _State`**: matches the
  `observability/tracing.py` pattern adopted earlier — keeps ruff
  `PLW0603` clean without sacrificing the singleton semantics
  purgatory needs to share circuit state across requests.

## How to validate locally
```pwsh
cd backend
uv run pytest -q
uv run ruff check .
uv run mypy src
```
