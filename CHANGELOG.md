# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste
arquivo.

O formato segue [Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere a [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/).

## [Unreleased]

_(nada ainda)_

---

## [1.0.0] — 2026-05-18

Primeira release pública do **SRM Credit Engine**. Reúne quinze
etapas de desenvolvimento incremental — modelagem, backend, domínio
hexagonal, API REST, relatórios analíticos, observabilidade,
resiliência, frontend, Docker, CI/CD, documentação arquitetural,
README final e tag de release.

### Added

#### Backend (Python 3.12 + FastAPI)
- Esqueleto FastAPI com Pydantic v2, settings tipadas, health checks
  (`/health`, `/health/ready`) e tratamento centralizado de erros.
- Domínio puro em arquitetura hexagonal (ver
  [ADR-002](docs/adr/ADR-002-hexagonal-architecture.md)):
  entidades `Assignor`, `Receivable`, `Settlement`, `ExchangeRate`,
  `ProductType`, value objects `Money` (Decimal-string) e `Cnpj`,
  portas `Protocol` para repositórios e conversor de câmbio.
- Strategy Pattern para precificação (juros simples e compostos)
  com cálculo determinístico via `Decimal` e arredondamento
  bancário (`ROUND_HALF_EVEN`) — ver
  [ADR-003](docs/adr/ADR-003-decimal-money.md).
- Camada de infraestrutura: SQLAlchemy 2.0 async + asyncpg,
  repositórios implementando as portas, migrations via alembic.
- Cache transacional de cotações de câmbio em PostgreSQL com TTL
  configurável.
- Camada de resiliência empilhada
  (`cache(DB) → circuit-breaker → retry → HTTP`) usando tenacity
  e purgatory — ver
  [ADR-004](docs/adr/ADR-004-resilience-layering.md).
- API REST `/api/v1` com routers para assignors, product types,
  receivables, pricing, exchange rates, settlements e reports.
- Relatórios analíticos com SQL nativo otimizado (bypass
  consciente do domínio para queries agregadas).
- Observabilidade: OpenTelemetry (traces + métricas) + Prometheus
  exporter em `/metrics` + structlog JSON com correlação por
  `trace_id` — ver
  [ADR-005](docs/adr/ADR-005-observability-stack.md).
- Cobertura de testes ≥ 80% como gate de CI; testes unitários de
  domínio, property-based para invariantes de `Money` e pricing,
  testes de integração para repositórios.

#### Frontend (React 19 + TypeScript + Vite + Tailwind v4)
- SPA com TanStack Query 5 para fetch remoto, TanStack Table 8
  para grids paginadas e ordenáveis, Zustand 5 para estado global,
  axios com interceptors traduzindo erros para `ApiClientError`.
- Decimal-string fim-a-fim usando `decimal.js`; apresentação via
  `Intl.NumberFormat`.
- Painel do Operador (carteira agregada, KPIs, filtros) e Grid de
  Transações com paginação server-side.
- Testes com vitest + axios-mock-adapter; gate de CI via
  `prettier --check`, ESLint, `tsc --noEmit`, `vitest run` e
  `vite build`.

#### Orquestração e operação
- `docker-compose.yml` com três serviços: PostgreSQL 16
  (healthcheck + volume named), backend (FastAPI/Uvicorn,
  `depends_on: service_healthy`) e frontend
  (nginx 1.27-alpine como reverse proxy do SPA com fallback
  e proxy `/api/` para o backend).
- Imagens Docker multi-stage para backend (uv builder → slim
  runtime, usuário não-root) e frontend (node:22-alpine builder →
  nginx:1.27-alpine runtime).
- `.env.example` na raiz, no backend e no frontend; configuração
  100% via variáveis de ambiente.

#### CI/CD
- Três workflows GitHub Actions path-filtered:
  `backend.yml` (`ruff check`, `ruff format --check`, `mypy strict`,
  `pytest` com cobertura ≥ 80%),
  `frontend.yml` (`prettier --check`, `eslint`, `tsc --noEmit`,
  `vitest run`, `vite build`) e
  `docker.yml` (build paralelo de imagens com cache GHA + validação
  de `docker compose config`).
- `.pre-commit-config.yaml` com hooks de hygiene + ruff lint/format
  no backend + prettier/eslint no frontend.

#### Documentação
- Seis ADRs (Architecture Decision Records) em
  [docs/adr/](docs/adr/) cobrindo estratégia de branching,
  arquitetura hexagonal, decimal-string, camadas de resiliência,
  stack de observabilidade e postura de multi-tenancy.
- Três diagramas C4 (Contexto, Containers, Componentes) em
  Mermaid nativo do GitHub —
  [docs/architecture/](docs/architecture/).
- Documento de escala com sete degraus e métricas-gatilho
  ([high-scale.md](docs/architecture/high-scale.md)).
- Nota sobre EDA com o padrão Transactional Outbox como caminho
  mínimo ([eda.md](docs/architecture/eda.md)).
- Cinco runbooks de gestão de crise
  ([runbooks/](docs/architecture/runbooks/)): FX outage, DB outage,
  latency spike, migration failure e tenant leak.
- `README.md` da raiz como ponto de entrada de produção e
  `AI_USAGE.md` (raiz) documentando o uso de IA com salvaguardas e
  limitações.
- Protocolo de hotfix com receita pedagógica em
  [docs/HOTFIX_PROTOCOL.md](docs/HOTFIX_PROTOCOL.md).
- Critérios de aceite consolidados em
  [docs/acceptance-criteria.md](docs/acceptance-criteria.md)
  cobrindo usabilidade, segurança, desempenho e escalabilidade.

#### Versionamento
- Tag anotada `v1.0.0` em `main`.

### Quality gates atendidos

- Backend lint (ruff), format (ruff), type check (`mypy --strict`).
- Backend testes com `pytest --cov-fail-under=80`.
- Frontend format (prettier), lint (eslint), type check
  (`tsc --noEmit`), testes (vitest), build (vite).
- Docker: imagens backend e frontend constroem sem warnings;
  `docker compose config --quiet` valida o stack.

### Referências

- Plano de execução por etapas:
  [docs/PLAN.md](docs/PLAN.md).
- Histórico de commits:
  [docs/COMMITS.md](docs/COMMITS.md).
- Descrições dos PRs:
  [docs/pull-requests/](docs/pull-requests/).

[Unreleased]: https://github.com/leduarte01/srm-credit-engine/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/leduarte01/srm-credit-engine/releases/tag/v1.0.0
