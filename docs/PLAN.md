# Plano de Execução — SRM Credit Engine

> Documento vivo. Cada etapa termina com 1+ commits seguindo **Conventional Commits**.
> Branches `feat/*`, `fix/*`, `docs/*`, `chore/*`, `ci/*`, `build/*`, `test/*`, `perf/*`.
> Estratégia de branching: **GitHub Flow** (ver [adr/ADR-001-branching-strategy.md](adr/ADR-001-branching-strategy.md)).

## Stack

| Camada                  | Tecnologia                                                       |
| ----------------------- | ---------------------------------------------------------------- |
| API                     | FastAPI (async)                                                  |
| Schemas                 | Pydantic v2                                                      |
| ORM                     | SQLAlchemy 2.0 async + asyncpg                                   |
| Migrations              | Alembic                                                          |
| Banco                   | PostgreSQL 16                                                    |
| SQL nativo (relatórios) | asyncpg direto                                                   |
| Testes                  | pytest + pytest-asyncio + hypothesis + pytest-cov                |
| Logs                    | structlog (JSON)                                                 |
| Métricas/Traces         | OpenTelemetry + prometheus-client                                |
| Resiliência             | tenacity (retry) + purgatory (circuit breaker)                   |
| Lint/Format             | Ruff + mypy --strict                                             |
| Pacotes                 | uv                                                               |
| Pre-commit              | pre-commit framework                                             |
| Frontend                | React 18 + TS + Vite + Tailwind + TanStack Query/Table + Zustand |
| Infra                   | Docker Compose                                                   |
| CI/CD                   | GitHub Actions                                                   |
| Branching               | GitHub Flow                                                      |

## Etapas

| #   | Etapa                                                             | Branch                   | Status |
| --- | ----------------------------------------------------------------- | ------------------------ | ------ |
| 0   | Bootstrap                                                         | `chore/bootstrap`        | ✅     |
| 1   | Modelagem de dados (ER + DDL)                                     | `feat/data-model`        | ✅     |
| 2   | Backend — esqueleto + config + Money/exceptions                   | `feat/backend-bootstrap` | ✅     |
| 3   | Domínio: entidades + Strategy Pattern + Currency Engine           | `feat/domain-pricing`    | ✅     |
| 4   | Infra: SQLAlchemy + repositórios + Alembic                        | `feat/infrastructure`    | ✅     |
| 5   | Aplicação: API REST + Swagger + exception handler + validações    | `feat/api-rest`          | ✅     |
| 6   | Extrato analítico com SQL nativo                                  | `feat/analytical-report` | ✅     |
| 7   | Testes unitários (Strategy + invariantes + property-based)        | `test/unit-coverage`     | ✅     |
| 8   | Observabilidade (structlog + OTel + Prometheus)                   | `feat/observability`     | ✅     |
| 9   | Resiliência (retry + circuit breaker no FX feed)                  | `feat/resilience`        | ✅     |
| 10  | Frontend (Painel do Operador + Grid de Transações)                | `feat/frontend`          | ✅     |
| 11  | Docker Compose (stack completa)                                   | `build/docker`           | ✅     |
| 12  | CI/CD + Pre-commit hooks                                          | `ci/github-actions`      | ✅     |
| 13  | ADRs + C4 + High-Scale + EDA + Crisis Mgmt + Acceptance Criteria  | `docs/architecture`      | ✅     |
| 14  | README final + AI_USAGE                                           | `docs/readme-final`      | ✅     |
| 15  | Tag `v1.0.0` + simulação de hotfix (`git revert` / `cherry-pick`) | `release/v1.0.0`         | ✅     |

## Melhorias pós-v1.0.0

| #   | Melhoria                                                                                                  | Branch                          | Status                        |
| --- | --------------------------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------- |
| M1  | Modal "Novo Recebível" (form completo) + botão "Liquidar" inline na tabela                                | `feat/frontend-receivable-crud` | ✅ Implementado (PR #23)      |
| M2  | Página Cedentes — listar + criar (nome, documento, limite de crédito)                                     | `feat/frontend-config-pages`    | ✅ Implementado (PR #22)      |
| M3  | Página Taxas de Câmbio — listar + criar par/taxa/validade                                                 | `feat/frontend-config-pages`    | ✅ Implementado (PR #22)      |
| M4  | PricingSimulator: trocar `input` livre por `<select>` com os 3 produtos e spreads como hint               | `feat/frontend-receivable-crud` | ✅ Implementado (PR #21)      |
| M5  | Grid: adicionar controles Prev/Next + "Exibindo X–Y de Z" para tornar paginação server-side visível na UI | `feat/frontend-receivable-crud` | ✅ Implementado (PR #21)      |
| M6  | Moeda: trocar `input` livre por `<select>` BRL/USD no simulador e nos filtros                             | `feat/frontend-receivable-crud` | ✅ Implementado (PR #21)      |
| M7  | Cotação FX em tempo real (fawazahmed0/exchange-api) com fallback DB→live, toggle no simulador             | `feat/live-fx-rate`             | ✅ Implementado (PRs #24–#27) |
| M8  | Upload em lote de recebíveis via CSV (drag-and-drop + validação linha a linha)                            | `feat/batch-upload-csv`         | ✅ Implementado (PR #28)      |

## Releases

| Tag      | Data       | Conteúdo                                                                     |
| -------- | ---------- | ---------------------------------------------------------------------------- |
| `v1.0.0` | 2026-05-18 | Primeira release pública (Etapas 0–15). Ver [CHANGELOG.md](../CHANGELOG.md). |
| `v1.1.0` | 2026-05-19 | Melhorias M1–M8 + CD via EasyPanel + i18n + dashboard. PRs #18–#29.          |
