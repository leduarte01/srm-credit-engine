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
- `fix(backend): copy README.md so hatchling can build the wheel during uv sync`
- `Merge PR #14: ci/cd (github actions + pre-commit)`

### Etapa 13 — Documentação de Arquitetura (`docs/architecture` → `main`)

- `docs(adr): add ADR-002 hexagonal architecture`
- `docs(adr): add ADR-003 decimal money as string`
- `docs(adr): add ADR-004 resilience layering`
- `docs(adr): add ADR-005 observability stack`
- `docs(adr): add ADR-006 multi-tenancy posture`
- `docs(architecture): add c4 context, container and component diagrams`
- `docs(architecture): add high-scale and eda notes`
- `docs(architecture): add crisis management runbooks`
- `docs: add PR-015 description and log etapa 13`
- `Merge PR #15: architecture documentation (ADRs + C4 + high-scale + EDA + runbooks)`

### Etapa 14 — README final + AI_USAGE (`docs/readme-final` → `main`)

- `docs: rewrite root README as production-grade entry point`
- `docs(frontend): replace Vite template README with project-specific content`
- `docs: add AI_USAGE describing how AI tooling was used`
- `docs: add PR-016 description and log etapa 14`
- `Merge PR #16: final README + AI_USAGE`

### Etapa 15 — Release v1.0.0 + hotfix protocol (`release/v1.0.0` → `main`)

- `docs(release): add CHANGELOG following keep-a-changelog with v1.0.0 entry`
- `docs: add HOTFIX_PROTOCOL with three variants and worked example`
- `docs: mark all roadmap stages complete in PLAN`
- `docs: add PR-017 description and log etapa 15`
- `docs: add acceptance criteria covering usability/security/perf/scale`
- `docs(hotfix): clarify worked example is pedagogical and not applied`
- `docs(ai): move AI_USAGE.md to repository root per case spec`
- `docs(adr-006): clarify tenant_id column not yet present in schema`
- `docs: add retroactive PR-004 description for lint/lockfile hotfix`
- `docs: update PR-017 description with QA fixes`
- `Merge PR #17: release v1.0.0 + hotfix protocol + QA fixes`
- `release: tag v1.0.0` _(tag anotada em main após o merge)_

---

## Pós-v1.0.0 — Melhorias e operacionalização

### Etapa 16 — Deploy (CD) e correções de infra

- `fix(nginx): add Docker DNS resolver and explicit rewrite for /api proxy`
- `fix(nginx): use full EasyPanel Swarm service name for backend upstream`
- `fix(frontend): strip /api prefix in nginx proxy and vite dev rewrite`
- `Merge PR #14 + PR #15` _(internal PR-018)_
- `build(ci): add EasyPanel deploy webhook after CI passes`
- `style: format README.md with prettier`
- `style: format frontend/README.md with prettier`
- `Merge PR #16` _(internal PR-019)_

### Etapa 17 — Melhorias de UX no painel

- `feat(frontend): add sidebar layout and KPI status cards to dashboard`
- `Merge PR #17` _(internal PR-020)_
- `feat(frontend): add PT-BR/EN language toggle and in-app help modal`
- `fix(frontend): correct default product code in PricingSimulator`
- `Merge PR #18 + PR #20` _(internal PR-021)_
- `feat(backend): seed currency and product-type catalog`
- `fix(backend): correct product-type codes to match pricing strategies`
- `style(backend): apply ruff format to seed migration`
- `style(backend): fix ruff E501 line too long in seed migration`
- `Merge PR #19` _(internal PR-022)_

### Etapa 18 — CRUD frontend (M1–M6)

- `feat(frontend): replace product_code input with select showing strategy spreads`
- `feat(frontend): add server-side pagination controls to receivable grid`
- `feat(frontend): replace currency text input with BRL/USD select`
- `style(frontend): apply prettier formatting to DashboardPage`
- `fix(frontend): remove duplicate Receivable import in DashboardPage`
- `Merge PR #21` _(internal PR-023 — M4+M5+M6)_
- `feat(frontend): M2+M3 – Assignors and Exchange Rates pages`
- `Merge PR #22` _(internal PR-024)_
- `feat(frontend): add New Receivable modal with full form and POST /receivables integration`
- `Merge PR #23` _(internal PR-025 — M1)_

### Etapa 19 — Cotação FX em tempo real (M7)

- `feat: cotacao FX em tempo real via AwesomeAPI com fallback DB->live`
- `Merge PR #24` _(internal PR-026)_
- `fix(infra): catch all exceptions in LiveRateCurrencyConverter to avoid 500`
- `Merge PR #25`
- `fix(infra): add 60-second in-process TTL cache to LiveRateCurrencyConverter`
- `Merge PR #26`
- `fix(api): fall back to DB rate when live FX API returns 429`
- `fix(infra): replace AwesomeAPI with fawazahmed0/exchange-api (no rate limit)`
- `style(lint): fix ruff errors in pricing router and live_rate_converter`
- `fix(types): add type arguments to dict return type in live_rate_converter`
- `fix(types): use dict[str, Any] in _fetch_base_rates to satisfy mypy strict`
- `Merge PR #27` _(internal PR-027 — hardening)_

### Etapa 20 — Upload em lote + revisão pós-v1.0.0

- `feat(frontend): add batch CSV upload modal for bulk receivable import`
- `style(frontend): fix prettier formatting in DashboardPage`
- `style(frontend): remove nullish coalescing from JSX text node`
- `fix(types): cast Object.fromEntries via unknown to satisfy tsc in BatchUploadModal`
- `Merge PR #28` _(internal PR-028 — M8)_
- `docs: update PLAN.md – mark M1-M8 complete with PR references`
- `docs: revisao end-to-end pos-v1.0.0`
- `Merge PR #29` _(internal PR-029)_
- `release: tag v1.1.0` _(tag anotada em main após o merge)_
