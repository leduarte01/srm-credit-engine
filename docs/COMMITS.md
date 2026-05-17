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
