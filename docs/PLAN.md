# Plano de Execução — SRM Credit Engine

> Documento vivo. Cada etapa termina com 1+ commits seguindo **Conventional Commits**.
> Branches `feat/*`, `fix/*`, `docs/*`, `chore/*`, `ci/*`, `build/*`, `test/*`, `perf/*`.
> Estratégia de branching: **GitHub Flow** (ver [adr/0005-branching-strategy.md](adr/0005-branching-strategy.md)).

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI (async) |
| Schemas | Pydantic v2 |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Migrations | Alembic |
| Banco | PostgreSQL 16 |
| SQL nativo (relatórios) | asyncpg direto |
| Testes | pytest + pytest-asyncio + hypothesis + pytest-cov |
| Logs | structlog (JSON) |
| Métricas/Traces | OpenTelemetry + prometheus-client |
| Resiliência | tenacity (retry) + purgatory (circuit breaker) |
| Lint/Format | Ruff + mypy --strict |
| Pacotes | uv |
| Pre-commit | pre-commit framework |
| Frontend | React 18 + TS + Vite + Tailwind + TanStack Query/Table + Zustand |
| Infra | Docker Compose |
| CI/CD | GitHub Actions |
| Branching | GitHub Flow |

## Etapas

| # | Etapa | Branch | Status |
|---|---|---|---|
| 0 | Bootstrap | `chore/bootstrap` | 🟡 em andamento |
| 1 | Modelagem de dados (ER + DDL) | `feat/data-model` | ⏳ |
| 2 | Backend — esqueleto + config + Money/exceptions | `feat/backend-bootstrap` | ⏳ |
| 3 | Domínio: entidades + Strategy Pattern + Currency Engine | `feat/domain-pricing` | ⏳ |
| 4 | Infra: SQLAlchemy + repositórios + Alembic | `feat/infrastructure` | ⏳ |
| 5 | Aplicação: API REST + Swagger + exception handler + validações | `feat/api-rest` | ⏳ |
| 6 | Extrato analítico com SQL nativo | `feat/analytical-report` | ⏳ |
| 7 | Testes unitários (Strategy + invariantes + property-based) | `test/unit-coverage` | ⏳ |
| 8 | Observabilidade (structlog + OTel + Prometheus) | `feat/observability` | ⏳ |
| 9 | Resiliência (retry + circuit breaker no FX feed) | `feat/resilience` | ⏳ |
| 10 | Frontend (Painel do Operador + Grid de Transações) | `feat/frontend` | ⏳ |
| 11 | Docker Compose (stack completa) | `build/docker` | ⏳ |
| 12 | CI/CD + Pre-commit hooks | `ci/github-actions` | ⏳ |
| 13 | ADRs + C4 + High-Scale + EDA + Crisis Mgmt + Acceptance Criteria | `docs/senior-deliverables` | ⏳ |
| 14 | README final + AI_USAGE | `docs/readme-final` | ⏳ |
| 15 | Tag `v1.0.0` + simulação de hotfix (`git revert` / `cherry-pick`) | `release/v1.0.0` | ⏳ |
