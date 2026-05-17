# PR #8 — Analytical reports: raw SQL surface under /v1/reports

## Summary
Adds the **analytical reporting** surface for the SRM Credit Engine, exposing
four read-only endpoints under `/v1/reports/*` powered by **raw SQL** executed
through the async engine (asyncpg in production, aiosqlite in the test
suite). Keeps the hexagonal boundary intact via a dedicated
`AnalyticsRepository` port and immutable DTOs in the domain layer.

## Scope
- Domain analytics package (`domain/analytics/`):
  - `dtos.py` — frozen dataclasses for periods and report rows
    (`ReportPeriod`, `VolumeByAssignorRow/Report`, `PnlByProductRow/Report`,
    `AgingBucketRow/Report`, `FxExposureRow/Report`).
  - `queries.py` — SQL constants written to be portable between PostgreSQL
    and SQLite, with named bind parameters and no ORM coupling.
- Domain port `AnalyticsRepository` (`domain/ports/analytics.py`) with four
  read methods.
- `SqlAnalyticsRepository` (`infrastructure/analytics_repository.py`) —
  executes the SQL via `AsyncSession.execute(text(...))`, defensively
  coerces driver-native scalars (UUID, Numeric) to typed Python values so
  `Decimal` precision is preserved across both dialects.
- API wiring: `AnalyticsRepoDep` in `api/v1/deps.py`; new
  `api/v1/routers/reports.py` registered on the v1 router; Pydantic v2
  response schemas in `api/v1/schemas/reports.py`.
- Endpoints:
  - `GET /v1/reports/volume-by-assignor?period_start&period_end&limit`
  - `GET /v1/reports/pnl-by-product?period_start&period_end`
  - `GET /v1/reports/aging-buckets?reference_date`
  - `GET /v1/reports/fx-exposure?reference_date`

## Quality gates
- **Ruff**: all checks passed
- **Mypy --strict**: 55 source files, no issues
- **Pytest**: **84/84** passing (was 77 before)
- **Coverage**: **88.15%** (gate ≥80%)

## New tests
`tests/integration/test_reports.py` drives each endpoint through the public
HTTP surface, creating and settling receivables via the API and asserting:
- aggregation correctness (`volume_by_assignor`, two settled receivables
  collapse into a single assignor row with summed face and present values);
- empty period yields zero rows;
- revenue derivation (`pnl_by_product`,
  `revenue = face_in_settlement_ccy − advanced`);
- bucket classification of `aging_buckets` against a fixed reference date,
  and exclusion of settled receivables;
- currency grouping of `fx_exposure` across BRL and USD;
- rejection of an inverted period (`422 VALIDATION_ERROR`).

## Architectural decisions
- **Raw SQL instead of ORM** for reports: aggregations, multi-join scans and
  bucketed `CASE` expressions are first-class in SQL and would be obscured
  by ORM relationships. Using `text()` over `AsyncSession` keeps the same
  driver (asyncpg in prod) without spinning up a parallel pool.
- **Portable SQL surface**: all statements avoid dialect-only constructs
  (`EXTRACT EPOCH`, `julianday`, `FILTER`), use named parameters and
  receive precomputed date boundaries from Python instead of date
  arithmetic in SQL. This lets the same query run on PostgreSQL and on the
  in-memory SQLite engine used by the integration suite.
- **Driver-native coercion at the boundary**: `_to_decimal` and `_to_uuid`
  normalize values returned by both drivers, ensuring downstream code
  always works with `Decimal` and `uuid.UUID` regardless of backend.
- **Hexagonal boundary preserved**: routers depend on the
  `AnalyticsRepository` port; the SQL implementation is the only artifact
  that knows about SQLAlchemy.
- **Half-open periods (`[start, end)`)** are validated in the DTO
  constructor, guaranteeing the invariant before the query is sent.

## Risks & follow-ups
- The aging report converts `face_value` only — it does not normalize
  outstanding amounts to a single currency. A future iteration will join
  the current FX table to express exposure in BRL alongside the native
  currency breakdown.
- A native asyncpg pool (bypassing SQLAlchemy entirely) could be wired for
  the heaviest reports later, but the current path already runs through
  asyncpg under the hood.
- Streaming CSV / pagination for very large result sets is out of scope and
  will be added with the frontend integration.

## Commits
- `feat(domain): add analytics port, DTOs and portable raw SQL queries`
- `feat(api): expose v1 reports endpoints backed by raw SQL analytics`
- `test(api): cover analytics reports endpoints end-to-end`
- `docs: add PR-008 description and log etapa 6`
- `Merge PR #8: analytical reports (/v1/reports with raw SQL)`
