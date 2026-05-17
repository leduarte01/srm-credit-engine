# PR #6 — Infrastructure: persistence, repositories and FX adapter

## Summary
Implements the persistence layer of the SRM Credit Engine using **SQLAlchemy 2.0
async** + **asyncpg** (PostgreSQL) with **aiosqlite** for portable in-memory
tests. Adds the **Alembic** async migration scaffold (baseline revision in
parity with `db/migrations/V1__init.sql`), the **repository ports** in the
domain layer and the **first concrete adapter** for the `CurrencyConverter`
port — proving the hexagonal architecture end-to-end.

## Scope
- ORM models (`infrastructure/models.py`) mapping every aggregate in the DDL,
  using portable types (`sa.Uuid`, `sa.JSON`, `sa.Numeric`) so SQLite can run
  the schema in unit tests while PostgreSQL keeps full fidelity.
- Async engine, sessionmaker and FastAPI `get_session` dependency
  (`infrastructure/database.py`), driven by `Settings.database_url`.
- Domain ports (`domain/ports/repositories.py`) declaring the contracts
  consumed by use-cases: `AssignorRepository`, `ProductTypeRepository`,
  `ExchangeRateRepository`, `ReceivableRepository`, `SettlementRepository`.
- SQLAlchemy repositories (`infrastructure/repositories.py`) implementing the
  ports with explicit **optimistic locking** on `Receivable.version` and
  uniqueness conflict translation to `ConcurrencyConflictError`.
- ORM↔Domain mappers (`infrastructure/mappers.py`) keeping the domain pure.
- `DatabaseCurrencyConverter` adapter — direct-rate lookup with inverse-rate
  fallback (`1/rate`); raises `ExchangeRateNotFoundError` on misses.
- Async Alembic env (`alembic/env.py`) wired to `Base.metadata` and reading
  `database_url` from `Settings`. Baseline revision `0001_initial_schema`
  replicates the SQL DDL for application-managed migrations.

## Quality gates
- **Ruff**: ✅ all checks passed
- **Mypy --strict**: ✅ 30 source files, no issues
- **Pytest**: ✅ **50/50** passing (was 39 before)
- **Coverage**: **91.47%** (gate ≥80%)

## New tests
- `tests/unit/conftest.py` — in-memory aiosqlite engine + seed (BRL/USD,
  products, USD→BRL FX rate).
- `tests/unit/test_repositories.py` — 7 tests covering CRUD, unique
  constraints, optimistic locking happy path + conflict, settlement audit
  trail round-trip.
- `tests/unit/test_database_currency_converter.py` — 4 tests covering
  passthrough, direct rate, inverse fallback, missing rate.

## Architectural decisions
- **Ports stay in the domain layer**; concrete repositories live in
  infrastructure. Services depend on Protocols, never on SQLAlchemy.
- **Optimistic locking** is enforced in the repository, not in the DB, so the
  domain stays portable. A row-level check (`expected_version == row.version`)
  is performed before flush.
- **Portable types** were chosen over PostgreSQL-only ones (`JSONB`, `UUID`
  native) so the same models drive aiosqlite tests and prod-grade Postgres.
- **Alembic baseline = DDL parity**, not autogenerate: keeps both
  application-managed migrations and the SQL-only path (`V1__init.sql`)
  consistent.

## Risks & follow-ups
- Real PostgreSQL integration tests will be added in Etapa 8 (with testcontainers
  or a docker-compose service) — the current suite exercises portable
  semantics only.
- Currency triangulation (e.g. EUR via USD) is deliberately out of scope; the
  seed only carries direct USD↔BRL pairs.

## Commits
- `chore(backend): add aiosqlite dev dependency for in-memory infra tests`
- `feat(infra): add async SQLAlchemy engine, session factory and ORM models`
- `feat(domain): add repository ports for hexagonal persistence`
- `feat(infra): add SQLAlchemy repositories with optimistic locking and mappers`
- `feat(infra): add DatabaseCurrencyConverter adapter implementing CurrencyConverter port`
- `build(alembic): bootstrap async Alembic with baseline schema revision`
- `test(infra): cover repositories and FX adapter against in-memory SQLite`
