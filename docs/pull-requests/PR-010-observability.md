# PR #10 — Observability: structured logs, traces and metrics

## Summary
Adds the **observability surface** of the SRM Credit Engine: structured
JSON logs with correlation ids, OpenTelemetry traces with OTLP/gRPC
export, and Prometheus metrics scraped at `/metrics`. Wired through a
single ASGI middleware so every HTTP request carries a stable
`request_id` and contributes to RED-style metrics.

## Scope
- New package `srm_credit_engine.observability/`:
  - `logging.py` — configures `structlog` (JSON in production, console
    in dev) and merges OpenTelemetry `trace_id` / `span_id` into every
    record via a custom processor.
  - `tracing.py` — installs an OTel `TracerProvider` with an OTLP/gRPC
    span exporter; idempotent and a no-op when disabled (tests/CI).
    Helper `instrument_app(app, engine)` attaches FastAPI and
    SQLAlchemy auto-instrumentation when needed.
  - `metrics.py` — Prometheus `CollectorRegistry` with five metrics:
    - `srm_http_requests_total{method, route, status}` (counter)
    - `srm_http_request_duration_seconds{method, route}` (histogram)
    - `srm_pricing_operations_total{product_code, outcome}` (counter)
    - `srm_settlement_operations_total{product_code, outcome}` (counter)
    - `srm_fx_lookups_total{base, quote, outcome}` (counter)
  - `middleware.py` — `ObservabilityMiddleware`: reads/generates
    `X-Request-ID`, binds it to `structlog.contextvars`, records HTTP
    counters and latency histogram, and echoes the id in the response.
- `main.py` wires the middleware, calls `configure_logging` and
  `configure_tracing` at startup, and exposes `/metrics` (gated by
  `settings.prometheus_enabled`).
- Domain instrumentation:
  - `pricing` and `settlements` routers increment
    `PRICING_OPERATIONS` / `SETTLEMENT_OPERATIONS` with the outcome
    label (`success` / `failure`).
  - `DatabaseCurrencyConverter` increments `FX_LOOKUPS` with
    `direct` / `inverse` / `missing` labels.

## Quality gates
- **Ruff**: passed
- **Mypy --strict**: 60 source files, no issues
- **Pytest**: **141/141** passing (was 133)
- **Coverage**: **89.31%** global (gate ≥80%)

## New tests
- `tests/integration/test_observability.py` — drives the FastAPI app
  end-to-end:
  - `/health` returns an `X-Request-ID` header.
  - Inbound `X-Request-ID` is echoed verbatim.
  - `/metrics` returns Prometheus text format containing the SRM
    metric families.
  - The HTTP counter for `GET /health, 200` strictly increases by two
    after two calls (parses the actual counter line, not a substring).
- `tests/unit/test_observability.py` — JSON log shape, console
  renderer smoke-test, `metrics_response()` payload, contextvars
  binding.

## Architectural decisions
- **structlog over `logging.LogRecord`**: structured key/value events
  are the canonical artefact for an APM pipeline; the JSON renderer
  drops a record-per-line directly consumable by Loki/Elastic without
  custom parsers.
- **Trace correlation as a structlog processor**: `_add_otel_context`
  reads the active span at emission time. Logs and traces share ids
  with zero per-call plumbing.
- **Custom Prometheus registry** (`REGISTRY`) instead of the global
  default: insulates tests from cross-suite counter bleed and lets the
  app expose only the SRM metric families.
- **Route template label, not raw path**: latency / counter metrics
  use `request.scope["route"].path` so dynamic ids (e.g.
  `/v1/receivables/{id}`) collapse into a single time series and avoid
  unbounded label cardinality.
- **Tracing is opt-out via `app_env`**: `configure_tracing` short-
  circuits in `test` and `ci` environments; no exporter is started, no
  background threads, no flaky network dependencies in tests.

## How to validate locally
```pwsh
cd backend
uv run pytest -q
uv run ruff check .
uv run mypy src
# In a separate shell, after starting the app:
curl http://localhost:8000/metrics | head
```
