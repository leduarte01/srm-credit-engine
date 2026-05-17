# PR #7 — API REST v1: routers, schemas and OpenAPI surface

## Summary
Exposes the SRM Credit Engine domain as a versioned **REST API under `/v1/*`**
using **FastAPI** and **Pydantic v2** schemas. Wires together the persistence
layer, the pricing service and the domain aggregates behind a thin HTTP
boundary, with a uniform JSON error envelope, request-payload validation and
auto-generated **OpenAPI / Swagger** documentation at `/docs`.

## Scope
- `api/v1/` package: routers, schemas, dependency wiring and centralized
  exception handlers.
- Routers (one per aggregate / use-case):
  - `assignors` — create / list / get-by-id / get-by-document
  - `product_types` — list / get-by-code (catalog)
  - `exchange_rates` — upsert / latest / point-in-time / history
  - `receivables` — create / list with filters + pagination / get / cancel
  - `pricing` — simulate (price without persisting)
  - `settlements` — settle (atomic price+persist with event log) / get
  - `meta` — list registered pricing strategies
- Pydantic v2 schemas with `from_attributes=True` and a typed `MoneySchema`
  serializer for the `Money` value object; `PageResponse[T]` envelope for
  paginated lists.
- Repository port extensions:
  - `AssignorRepository.get_id_by_document`
  - `ReceivableRepository.list` accepting a `ReceivableFilter` dataclass and
    returning a `Page[Receivable]` (offset / limit + total).
  - `add(...)` methods on receivable / settlement repositories for new
    aggregates created over HTTP.
- Domain exception additions for missing aggregates
  (`AssignorNotFoundError`, `ProductTypeNotFoundError`,
  `SettlementNotFoundError`) — each carrying a stable error `code` and the
  proper HTTP status.
- Uniform error envelope `{code, message, details?}` produced by exception
  handlers for `DomainError`, `RequestValidationError`, `NoResultFound`,
  generic `ValueError` and unhandled exceptions.
- CORS middleware driven by `Settings.cors_origins_list`.
- `app.openapi()` exposes **14** documented paths grouped by tag
  (`assignors`, `product-types`, `fx-rates`, `receivables`, `pricing`,
  `settlements`, `meta`) and reachable from `/docs`.

## Quality gates
- **Ruff**: ✅ all checks passed
- **Mypy --strict**: ✅ 48 source files, no issues
- **Pytest**: ✅ **77/77** passing (was 50 before)
- **Coverage**: **87.37%** (gate ≥80%)

## New tests
End-to-end integration suite using `httpx.AsyncClient` over `ASGITransport`,
with a per-test in-memory `aiosqlite` engine and a `get_session` dependency
override that opens one transaction per request:
- `tests/integration/test_health.py` — liveness and OpenAPI registration.
- `tests/integration/test_assignors.py` — create / lookup / 404 mapping.
- `tests/integration/test_product_types.py` — catalog listing and lookup.
- `tests/integration/test_exchange_rates.py` — upsert, history,
  same-currency rejection (422), missing-rate 404.
- `tests/integration/test_receivables.py` — full lifecycle with filters,
  pagination and cancellation.
- `tests/integration/test_pricing_and_settlement.py` — pricing simulation
  parity vs. settle endpoint, FX application on USD products, audit-log
  assertion (`CREATED → PRICED → FX_APPLIED → SETTLED`).

## Architectural decisions
- **Hexagonal boundary preserved**: the API depends on domain ports
  (`SessionDep`, repository protocols, `PricingService`) injected via
  FastAPI `Depends`. No SQLAlchemy types leak into routers or schemas.
- **Pydantic v2 with `model_validate`** is used at the response boundary —
  domain aggregates stay free of serialization concerns; `from_attributes`
  + a dedicated `MoneySchema` keep `Decimal` precision intact in the wire
  format.
- **`Annotated[T, Query(...)]` pattern** for query parameters avoids the
  `B008` lint and prevents the well-known FastAPI bug where a shared
  `Query()` default instance breaks parameter binding.
- **Pagination via `Page[T]` / `PageResponse[T]`** keeps the contract
  generic and uniform across endpoints.
- **Atomic settle flow** (`POST /v1/settlements`): the route loads the
  aggregate, runs `PricingService.price`, transitions the receivable
  (`mark_as_priced` → `mark_as_settled`) and persists settlement + events
  inside a single transactional unit-of-work.
- **Error envelope is stable and code-driven**: every domain error carries
  a machine-readable `code` (`RECEIVABLE_NOT_FOUND`,
  `INVALID_RECEIVABLE_STATE`, `CONCURRENCY_CONFLICT`, …) so clients can
  branch on `error.code` instead of parsing messages.

## Risks & follow-ups
- AuthN / AuthZ is intentionally out of scope; the API is open in this PR
  and will gain JWT-based auth in a later etapa.
- Rate limiting and request-id propagation will be added together with the
  observability stack (Etapa 7).
- The analytical / reporting endpoints (raw SQL with `asyncpg`) are
  scheduled for Etapa 6 and will live under `/v1/reports/*`.

## Commits
- `feat(domain): extend repository ports with list and add operations`
- `feat(api): expose v1 REST surface with routers, schemas and error handling`
- `test(api): cover happy paths and error mapping for v1 endpoints`
- `docs: add PR-007 description and log etapa 5`
- `Merge PR #7: REST API v1 (FastAPI routers + OpenAPI + integration tests)`
