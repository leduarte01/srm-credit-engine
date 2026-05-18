# Histórico de Commits

Este documento traz a sequência de commits planejada. Os commits reais são feitos durante o desenvolvimento — este arquivo é atualizado ao final de cada etapa para fins de rastreabilidade.

## Convenção

[Conventional Commits 1.0.0](https://www.conventionalcommits.org/).

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

## Histórico

### Etapa 0 — Bootstrap (`chore/bootstrap` → `main`)
- `chore: initialize repository structure and plan`
- `chore: add gitignore and editorconfig for Python + Node stack`
- `docs: add commits log placeholder`
- `chore: add gitattributes and PR-001 description`

### Etapa 1 — Modelagem de dados (`feat/data-model` → `main`)
- `docs(data): add ER diagram for credit engine`
- `feat(db): create initial schema with currencies, products, receivables, settlements`
- `docs: add PR-002 description`
- `Merge PR #2: data model (ER + DDL)`

### Etapa 2 — Backend Bootstrap (`feat/backend-bootstrap` → `main`)
- `chore(backend): scaffold python project with uv, ruff, mypy strict, pytest`
- `feat(api): add FastAPI app skeleton with settings and healthcheck`
- `feat(domain): add Money value object and DomainError hierarchy`
- `test(domain): cover Money invariants and decimal safety`
- `docs: add PR-003 description`
- `Merge PR #3: backend bootstrap (Python + FastAPI scaffolding)`

### Manutenção — Lint, lockfile e specs (`chore/lint-and-lockfile` → `main`)
- `fix(quality): extract ISO-4217 length constant and drop obsolete ruff rules`
- `build(backend): commit uv lockfile for reproducible installs`
- `docs: preserve original technical case specification`
- `Merge PR #4: lint fixes + lockfile + case spec preservation`

### Etapa 3 — Entidades de domínio + Strategy de pricing (`feat/domain-pricing` → `main`)
- `feat(domain): add Currency, ProductType, Assignor and ExchangeRate entities`
- `feat(domain): add Receivable aggregate with optimistic locking and state machine`
- `feat(domain): add Settlement aggregate and immutable SettlementEvent log`
- `feat(pricing): add PricingStrategy protocol and PricingResult DTO`
- `feat(pricing): implement Duplicata, Cheque and ContratoUsd strategies`
- `feat(pricing): add PricingStrategyResolver registry (Open/Closed)`
- `feat(domain): add CurrencyConverter port and PricingService orchestrator`
- `test(domain): cover all entities, strategies and pricing service flows`
- `docs: add PR-005 description`
- `Merge PR #5: domain entities and pricing strategy`

### Etapa 4 � Infraestrutura de persist�ncia (eat/infrastructure ? main)
- `chore(backend): add aiosqlite dev dependency for in-memory infra tests`
- `feat(infra): add async SQLAlchemy engine, session factory and ORM models`
- `feat(domain): add repository ports for hexagonal persistence`
- `feat(infra): add SQLAlchemy repositories with optimistic locking and mappers`
- `feat(infra): add DatabaseCurrencyConverter adapter implementing CurrencyConverter port`
- `build(alembic): bootstrap async Alembic with baseline schema revision`
- `test(infra): cover repositories and FX adapter against in-memory SQLite`
- `docs: add PR-006 description`
- `Merge PR #6: infrastructure layer (SQLAlchemy + Alembic + repositories + FX adapter)`

### Etapa 5 — API REST + Swagger (`feat/api-rest` → `main`)
- `feat(domain): extend repository ports with list and add operations`
- `feat(api): expose v1 REST surface with routers, schemas and error handling`
- `test(api): cover happy paths and error mapping for v1 endpoints`
- `docs: add PR-007 description and log etapa 5`
- `Merge PR #7: REST API v1 (FastAPI routers + OpenAPI + integration tests)`

### Etapa 6 — Extrato analítico com SQL nativo (`feat/analytical-report` → `main`)
- `feat(domain): add analytics port, DTOs and portable raw SQL queries`
- `feat(api): expose v1 reports endpoints backed by raw SQL analytics`
- `test(api): cover analytics reports endpoints end-to-end`
- `docs: add PR-008 description and log etapa 6`
- `Merge PR #8: analytical reports (/v1/reports with raw SQL)`

### Etapa 7 � Testes unit�rios + property-based (`test/unit-coverage` ? `main`)
- `test(domain): add property-based tests for Money invariants`
- `test(domain): cover entity invariants and Receivable state machine`
- `test(domain): add property-based tests for pricing strategies and service`
- `docs: add PR-009 description and log etapa 7`
- `Merge PR #9: unit coverage (property-based tests for domain invariants)`

### Etapa 8 � Observabilidade (`feat/observability` ? `main`)
- `feat(observability): add structlog, OpenTelemetry and Prometheus building blocks`
- `feat(api): wire observability middleware, /metrics endpoint and domain counters`
- `test(observability): cover logging, metrics endpoint and request id propagation`
- `docs: add PR-010 description and log etapa 8`
- `Merge PR #10: observability (structlog + OTel + Prometheus)`

### Etapa 9 — Resiliência (`feat/resilience` → `main`)
- `feat(resilience): add tenacity retry helper for transient infrastructure failures`
- `feat(resilience): add purgatory circuit breaker factory excluding domain errors`
- `feat(resilience): wrap currency converter with retry and circuit breaker`
- `feat(api): wire ResilientCurrencyConverter into v1 dependencies`
- `test(resilience): cover retry policy, circuit breaker and resilient converter`
- `docs: add PR-011 description and log etapa 9`
- `Merge PR #11: resilience (tenacity retries + purgatory circuit breakers)`

### Etapa 10 — Frontend (`feat/frontend` → `main`)
- `chore(frontend): scaffold vite + react 19 + ts project with tailwind v4`
- `chore(frontend): wire vitest, jsdom setup and dev proxy for the api`
- `feat(frontend): add typed axios client and endpoints for the credit api`
- `feat(frontend): add formatting helpers, query hooks and zustand ui store`
- `feat(frontend): add operator panel with receivable grid and pricing simulator`
- `test(frontend): cover api error wrapping and receivable table rendering`
- `docs: add PR-012 description and log etapa 10`
- `Merge PR #12: frontend (operator panel with pricing simulator and receivables grid)`

### Etapa 11 — Docker Compose (`build/docker` → `main`)
- `build(backend): add multi-stage dockerfile with uv and migration entrypoint`
- `build(frontend): add multi-stage dockerfile with nginx serving the spa`
- `build(docker): add nginx config with /api reverse proxy and spa fallback`
- `build(compose): add end-to-end stack with postgres, backend and frontend`
- `docs: add PR-013 description and log etapa 11`
- `Merge PR #13: docker (end-to-end local stack with compose)`

### Etapa 12 — CI/CD + Pre-commit (`ci/github-actions` → `main`)
- `style(backend): apply ruff format to align with the new ci gate`
- `style(frontend): apply prettier to align with the new ci gate`
- `ci(backend): add github actions workflow with ruff, mypy and pytest`
- `ci(frontend): add github actions workflow with prettier, eslint, vitest and build`
- `ci(docker): add workflow to build images and validate compose`
- `chore: add pre-commit config with ruff, prettier and hygiene hooks`
- `docs: add PR-014 description and log etapa 12`
- `Merge PR #14: ci/cd (github actions + pre-commit)`
