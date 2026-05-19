# SRM Credit Engine

> Plataforma de gestão de **cessão de crédito multimoedas** para
> **FIDCs** (Fundos de Investimento em Direitos Creditórios).
>
> Backend: **Python 3.12 + FastAPI** · DB: **PostgreSQL 16** ·
> Frontend: **React 19 + TypeScript + Vite + Tailwind v4** ·
> Orquestração: **Docker Compose** · Observabilidade: **OpenTelemetry +
> Prometheus + structlog**.

---

## Sumário

- [O que é](#o-que-é)
- [Validação contra o case](#validação-contra-o-case)
- [Stack e versões](#stack-e-versões)
- [Início rápido (Docker)](#início-rápido-docker)
- [Desenvolvimento local](#desenvolvimento-local)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Endpoints principais](#endpoints-principais)
- [Funcionalidades de produto](#funcionalidades-de-produto)
- [Qualidade e CI](#qualidade-e-ci)
- [Arquitetura](#arquitetura)
- [Decisões registradas (ADRs)](#decisões-registradas-adrs)
- [Operação em crise](#operação-em-crise)
- [Versionamento e releases](#versionamento-e-releases)
- [Uso de IA neste projeto](#uso-de-ia-neste-projeto)

---

## O que é

Sistema web para um FIDC operar o ciclo completo de cessão de crédito:

- **Cadastrar cedentes** (assignors) com KYC mínimo.
- **Lançar recebíveis** em qualquer moeda suportada.
- **Precificar** os recebíveis por juros simples ou compostos, com
  conversão cambial via provedor externo + cache + resiliência.
- **Liquidar** operações e manter audit trail imutável.
- **Visualizar a carteira agregada** em dashboards com filtros e
  exportações.

A regra de negócio é isolada em domínio puro (sem framework) seguindo
**arquitetura hexagonal** — ver
[ADR-002](docs/adr/ADR-002-hexagonal-architecture.md).

## Validação contra o case

O briefing original está em
[README_case_dev_srm.md](README_case_dev_srm.md). Mapa requisito ↔
implementação:

### Backend (seção 3 do case)

| #   | Requisito                                                                        | Onde foi atendido                                                                                                                                                                        |
| --- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Currency Engine** — armazenar/prover taxas FX e endpoint de atualização        | `infrastructure/database_currency_converter.py`, router `/fx-rates`, `/api/v1/exchange-rates`; integração ao vivo via `LiveRateCurrencyConverter` (CDN fawazahmed0) com fallback DB→live |
| 2   | **Strategy Pattern** para precificação por tipo de recebível                     | `domain/pricing/strategies/*` (Duplicata 1,5% a.m., Cheque 2,5% a.m., Contrato USD 1,2% a.m.); resolução em `PricingStrategyResolver`                                                    |
| 2   | Fórmula `VP = VF / (1 + base + spread)^prazo` + conversão cambial cross-currency | `domain/services/pricing_service.py`                                                                                                                                                     |
| 3   | Persistência relacional + ACID + sem race-condition                              | PostgreSQL 16 + SQLAlchemy 2.0 async + alembic; **optimistic locking** via coluna `version` em `Receivable`/`Settlement`                                                                 |
| 4   | **API RESTful** com verbos/códigos corretos + OpenAPI                            | FastAPI `/api/v1` com Swagger interativo em `/docs` e ReDoc em `/redoc`                                                                                                                  |
| 5   | **Extrato analítico** filtrado por período / cedente / moeda; SQL nativo         | `domain/analytics/*` + `infrastructure/analytics_repository.py` com SQL nativo (bypass do ORM) — router `/reports/*`                                                                     |
| 6   | **Arquitetura em camadas** (apresentação / negócio / persistência)               | Hexagonal: `api/` (adaptador IN) → `domain/` (regras puras) → `infrastructure/` (adaptadores OUT); relatórios bypassam negócio diretamente para SQL nativo                               |

### Frontend (seção 4)

| #   | Requisito                                                       | Onde foi atendido                                                                                                                                                       |
| --- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Painel do Operador** com simulação em tempo real              | `components/PricingSimulator.tsx` (POST `/pricing/simulate` debounced) + toggle de cotação ao vivo                                                                      |
| 2   | **Grid de Transações** paginada server-side + filtros dinâmicos | `pages/DashboardPage.tsx` + `components/ReceivableFilters.tsx` + `components/ReceivableTable.tsx` (TanStack Table + Query); paginação `Prev / Next / Exibindo X–Y de Z` |
| 3   | **Separação UI ↔ negócio/estado** + estado global               | TanStack Query (server state), Zustand (`store/uiStore.ts` para UI), componentes puros em `components/`, páginas compõem features                                       |

### Requisitos não-funcionais (seção 5)

| #   | Requisito                         | Onde foi atendido                                                                                                                            |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Tratamento de exceções resiliente | `api/v1/errors.py` (handlers globais traduzindo `DomainError`, `ValueError`, `IntegrityError` em 4xx tipados) + `ApiClientError` no frontend |
| 2   | Critérios de aceite               | [docs/acceptance-criteria.md](docs/acceptance-criteria.md) (usabilidade, segurança, desempenho, escalabilidade)                              |

### Senioridade — entregáveis acumulados (seção 6)

| Nível           | Item                                                 | Onde foi atendido                                                                                                                                                                    |
| --------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🟢 Júnior       | Commits atômicos + branches por feature              | [docs/COMMITS.md](docs/COMMITS.md) + histórico em PRs #1–#28                                                                                                                         |
| 🟢 Júnior       | Lógica de cálculo correta + ER + README "como rodar" | Testes property-based em `tests/unit/domain/pricing/`; [docs/ER.md](docs/ER.md); seção [Início rápido](#início-rápido-docker)                                                        |
| 🟡 Pleno        | Conventional Commits + PRs descritivos               | [docs/pull-requests/](docs/pull-requests/)                                                                                                                                           |
| 🟡 Pleno        | Docker + Docker Compose                              | `docker-compose.yml` + Dockerfiles multi-stage                                                                                                                                       |
| 🟡 Pleno        | Exception handlers globais + validações de input     | `api/v1/errors.py` + Pydantic v2 strict                                                                                                                                              |
| 🟡 Pleno        | Testes unitários da Strategy                         | `tests/unit/domain/pricing/test_strategies.py`                                                                                                                                       |
| 🔴 Sênior       | Git hooks (pre-commit)                               | `.pre-commit-config.yaml`                                                                                                                                                            |
| 🔴 Sênior       | SemVer tags                                          | Tag anotada `v1.0.0`                                                                                                                                                                 |
| 🔴 Sênior       | Interactive rebase / histórico limpo                 | Squash em PRs de fix; merges `--no-ff` em `main`                                                                                                                                     |
| 🔴 Sênior       | Diagramas C4 (1 e 2)                                 | [docs/architecture/c4-context.md](docs/architecture/c4-context.md) + [c4-containers.md](docs/architecture/c4-containers.md) + [c4-components.md](docs/architecture/c4-components.md) |
| 🔴 Sênior       | Observabilidade (logs / métricas / tracing)          | structlog JSON + Prometheus em `/metrics` + OTel; ADR-005                                                                                                                            |
| 🔴 Sênior       | CI/CD com testes e linter                            | `.github/workflows/{backend,frontend,docker}.yml`                                                                                                                                    |
| 🔴 Sênior       | Resiliência (retry / circuit breaker)                | `resilience/{retries,circuit_breaker,resilient_converter}.py` + ADR-004                                                                                                              |
| 🔴 Sênior       | Optimistic Locking                                   | Coluna `version` em `Receivable`/`Settlement` com check otimista em `UPDATE`                                                                                                         |
| 🟣 Especialista | Estratégia de branching justificada                  | [ADR-001](docs/adr/ADR-001-branching-strategy.md) — GitHub Flow                                                                                                                      |
| 🟣 Especialista | Simulação de crise (`revert` / `cherry-pick`)        | [docs/HOTFIX_PROTOCOL.md](docs/HOTFIX_PROTOCOL.md)                                                                                                                                   |
| 🟣 Especialista | ADRs                                                 | [docs/adr/](docs/adr/) — 6 ADRs                                                                                                                                                      |
| 🟣 Especialista | Design para alta escala (1M tx/min)                  | [docs/architecture/high-scale.md](docs/architecture/high-scale.md)                                                                                                                   |
| 🟣 Especialista | Modelagem de eventos (EDA)                           | [docs/architecture/eda.md](docs/architecture/eda.md) — Transactional Outbox                                                                                                          |

### Modelagem de dados (seção 7)

| Item        | Onde foi atendido                                      |
| ----------- | ------------------------------------------------------ |
| Diagrama ER | [docs/ER.md](docs/ER.md)                               |
| Scripts DDL | `backend/alembic/versions/*.py` (migrations canônicas) |

### Documentação de IA (seção 2)

| Item                                                     | Onde foi atendido          |
| -------------------------------------------------------- | -------------------------- |
| `AI_USAGE.md` com prompts, alucinações e análise crítica | [AI_USAGE.md](AI_USAGE.md) |

## Stack e versões

| Camada       | Tecnologia                                                                                            |
| ------------ | ----------------------------------------------------------------------------------------------------- |
| Linguagem    | Python 3.12.10 / TypeScript 5                                                                         |
| Backend      | FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · asyncpg · alembic                                      |
| Resiliência  | tenacity (retry) · purgatory (circuit breaker)                                                        |
| Observ.      | OpenTelemetry SDK · Prometheus exporter · structlog                                                   |
| Banco        | PostgreSQL 16 (alpine)                                                                                |
| Frontend     | React 19.2 · Vite 8 · TanStack Query/Table · Zustand · axios                                          |
| Estilo (FE)  | Tailwind CSS v4 (config inline; ver [ADR-003](docs/adr/ADR-003-decimal-money.md) p/ tipos monetários) |
| Testes       | pytest + coverage · vitest + axios-mock-adapter                                                       |
| Lint         | ruff · mypy strict · ESLint · Prettier                                                                |
| Build        | uv (Python) · npm + Vite (FE) · hatchling (wheel)                                                     |
| Orquestração | docker-compose v2; nginx 1.27-alpine como reverse proxy do SPA                                        |
| CI           | GitHub Actions (workflows por caminho) + pre-commit                                                   |

---

## Início rápido (Docker)

Pré-requisitos: **Docker** + **Docker Compose v2**.

```bash
# 1. Copiar variáveis padrão
cp .env.example .env

# 2. Subir a stack completa (db + backend + frontend)
docker compose up --build

# 3. Acessar
#   SPA      → http://localhost:8080
#   API      → http://localhost:8000/api/v1/
#   Health   → http://localhost:8000/health
#   Métricas → http://localhost:8000/metrics
```

A primeira subida aplica `alembic upgrade head` automaticamente
(controlado por `RUN_MIGRATIONS=true` no entrypoint do backend).

Parar e limpar:

```bash
docker compose down            # mantém volume
docker compose down -v         # apaga o volume pgdata
```

---

## Desenvolvimento local

### Backend

Pré-requisitos: **Python 3.12** + [**uv**](https://docs.astral.sh/uv/) +
PostgreSQL acessível (rode `docker compose up -d db` se preferir).

```bash
cd backend
uv sync --dev
cp .env.example .env

uv run alembic upgrade head
uv run uvicorn srm_credit_engine.main:app --reload --port 8000
```

Comandos úteis:

```bash
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mypy src                  # type check estrito
uv run pytest                    # testes + cobertura (gate 80%)
uv run pytest -m "not integration"
```

### Frontend

Pré-requisitos: **Node 22**.

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev          # http://localhost:5173 (proxy para http://localhost:8000)
```

Comandos úteis:

```bash
npm run lint
npm run format:check
npm run test         # vitest
npm run build        # vite build
```

### Pre-commit (opcional, recomendado)

```bash
pipx install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Estrutura do repositório

```
SRM/
├── backend/                     # FastAPI + domínio + infra
│   ├── src/srm_credit_engine/
│   │   ├── api/v1/              # routers, schemas, deps (composition root)
│   │   ├── domain/              # entities, value objects, ports, pricing
│   │   ├── infrastructure/      # ORM, repositories, mappers, cache FX
│   │   ├── resilience/          # retry + circuit breaker + decorator
│   │   ├── observability/       # OTel + Prometheus + structlog
│   │   └── main.py
│   ├── alembic/                 # migrations
│   ├── tests/
│   ├── Dockerfile               # multi-stage (uv builder → slim runtime)
│   └── pyproject.toml
├── frontend/                    # SPA React
│   ├── src/
│   ├── docker/nginx.conf        # reverse proxy + SPA fallback + /healthz
│   ├── Dockerfile               # multi-stage (node builder → nginx)
│   └── package.json
├── docs/
│   ├── PLAN.md                  # plano de execução por etapas
│   ├── COMMITS.md               # histórico de commits
│   ├── ER.md                    # modelo entidade-relacionamento
│   ├── adr/                     # Architecture Decision Records (001–006)
│   ├── architecture/            # C4 + high-scale + EDA + runbooks
│   ├── pull-requests/           # corpo dos PRs (PR-001…017)
│   ├── HOTFIX_PROTOCOL.md       # protocolo operacional de hotfix
│   └── acceptance-criteria.md   # critérios de aceite do produto
├── .github/workflows/           # backend, frontend, docker (CI)
├── .pre-commit-config.yaml
├── docker-compose.yml
├── CHANGELOG.md                 # Keep a Changelog 1.1.0
├── AI_USAGE.md                  # uso de IA no desenvolvimento
└── README.md                    # este arquivo
```

---

## Endpoints principais

Base path: `/api/v1`. OpenAPI interativo em `/docs`.

| Recurso             | Métodos                               | Descrição                                                      |
| ------------------- | ------------------------------------- | -------------------------------------------------------------- |
| `/assignors`        | GET, POST, GET/{id}, PATCH/{id}       | Cedentes (KYC + dados cadastrais)                              |
| `/product-types`    | GET                                   | Catálogo de tipos de produto                                   |
| `/receivables`      | GET, POST, GET/{id}, PATCH/{id}       | Recebíveis (POST em lote no frontend via CSV)                  |
| `/pricing/simulate` | POST                                  | Precifica recebível (simples/composto + FX cadastrado ou live) |
| `/fx-rates`         | GET, POST, GET/{base}/{quote}/history | Cotações de câmbio cadastradas + histórico                     |
| `/settlements`      | GET, POST                             | Liquidações (audit trail de eventos imutável)                  |
| `/reports/*`        | GET                                   | Sumarizações analíticas da carteira (SQL nativo)               |
| `/health`           | GET                                   | Liveness                                                       |
| `/health/ready`     | GET                                   | Readiness (ping no DB)                                         |
| `/metrics`          | GET                                   | Prometheus scrape                                              |

Valores monetários trafegam **sempre como string decimal** —
ver [ADR-003](docs/adr/ADR-003-decimal-money.md).

## Funcionalidades de produto

Além dos requisitos do case, foram adicionadas melhorias pós-v1.0.0
documentadas em [docs/PLAN.md](docs/PLAN.md):

- **Painel multimoeda (BRL/USD)** — selects fixos no simulador e nos
  filtros, evitando códigos arbitrários.
- **Modal "Novo Recebível"** com form completo + botão **"Liquidar"**
  inline na tabela de recebíveis.
- **Upload em lote via CSV** — drag-and-drop com validação linha a
  linha, relatório de erros e fallback de criação parcial. Exemplo
  em [scripts/receivables_sample.csv](scripts/receivables_sample.csv).
- **Cotação FX em tempo real** com toggle no `PricingSimulator`. Por
  padrão usa a taxa cadastrada; quando ausente faz fallback automático
  para a CDN [fawazahmed0/exchange-api](https://github.com/fawazahmed0/exchange-api)
  (sem auth, sem rate-limit) com cache in-process de 60 s e mirror
  Cloudflare Pages. A resposta indica `fx_rate_source: "database" | "live"`
  e a UI mostra um badge colorido.
- **Páginas de configuração** — Cedentes e Taxas de Câmbio (listar +
  criar) com formulários acessíveis e estado gerenciado por TanStack
  Query.
- **i18n PT/EN** com toggle persistente (Zustand) — todo o painel,
  modais e mensagens de erro têm chaves traduzidas em
  `frontend/src/lib/i18n.ts`.
- **Help modal contextual** explicando spreads, fórmula e fluxo de
  liquidação.

---

## Qualidade e CI

Três workflows path-filtered (`.github/workflows/`):

- **backend.yml** — `ruff check` + `ruff format --check` + `mypy strict`
  - `pytest` (cobertura ≥ 80%, falha CI abaixo).
- **frontend.yml** — `prettier --check` + `eslint` + `tsc --noEmit` +
  `vitest run` + `vite build`.
- **docker.yml** — build paralelo das imagens (cache `type=gha`) +
  `docker compose config --quiet`.

Localmente os mesmos gates rodam via **pre-commit** (`.pre-commit-config.yaml`).

Todos os PRs seguem **Conventional Commits 1.0.0** + descrição em
[docs/pull-requests/](docs/pull-requests/).

---

## Arquitetura

A arquitetura está documentada em **quatro eixos**:

1. **Decisões imutáveis** — [docs/adr/](docs/adr/).
2. **C4 (Contexto, Containers, Componentes)** — [docs/architecture/](docs/architecture/).
3. **Escala** — [docs/architecture/high-scale.md](docs/architecture/high-scale.md).
4. **EDA / Outbox** — [docs/architecture/eda.md](docs/architecture/eda.md).

Princípios não-negociáveis:

- **Domínio puro** não importa nada de infraestrutura.
- **Dinheiro é `Decimal`** backend, **string no JSON**, `decimal.js`
  no frontend.
- **Resiliência empilhada**: cache(DB) → breaker → retry → HTTP.
- **Tudo correlacionado por `trace_id`** (OTel) através dos logs
  (structlog) e métricas (Prometheus exemplars).

## Decisões registradas (ADRs)

| ID  | Título                                                                                    | Status |
| --- | ----------------------------------------------------------------------------------------- | ------ |
| 001 | [Branching Strategy: GitHub Flow](docs/adr/ADR-001-branching-strategy.md)                 | Aceito |
| 002 | [Arquitetura Hexagonal (Ports & Adapters)](docs/adr/ADR-002-hexagonal-architecture.md)    | Aceito |
| 003 | [Decimal serializado como string](docs/adr/ADR-003-decimal-money.md)                      | Aceito |
| 004 | [Camadas de resiliência](docs/adr/ADR-004-resilience-layering.md)                         | Aceito |
| 005 | [Observabilidade: OTel + Prometheus + structlog](docs/adr/ADR-005-observability-stack.md) | Aceito |
| 006 | [Multi-tenancy: single-DB com `tenant_id`](docs/adr/ADR-006-multi-tenancy.md)             | Aceito |

## Operação em crise

Runbooks em [docs/architecture/runbooks/](docs/architecture/runbooks/):

- **FX outage** — provedor de câmbio caído (P2).
- **DB outage** — PostgreSQL inacessível (P0).
- **Latency spike** — pico de p95 (P2/P1).
- **Migration failure** — alembic falhou em produção (P1).
- **Tenant leak** — suspeita de vazamento cross-tenant (P0).

Protocolo de hotfix (revert / cherry-pick) em
[docs/HOTFIX_PROTOCOL.md](docs/HOTFIX_PROTOCOL.md). Critérios de aceite
do produto em [docs/acceptance-criteria.md](docs/acceptance-criteria.md).

---

## Versionamento e releases

- **GitHub Flow** com merges `--no-ff` em `main` — ver
  [ADR-001](docs/adr/ADR-001-branching-strategy.md).
- **SemVer** (`vMAJOR.MINOR.PATCH`) com tag anotada por release.
- **Hotfix** segue protocolo `git revert` + `git cherry-pick`, sem
  branch de longa duração.
- **Plano de execução** versionado em [docs/PLAN.md](docs/PLAN.md);
  histórico de commits em [docs/COMMITS.md](docs/COMMITS.md).

## Uso de IA neste projeto

Este projeto foi desenvolvido com **assistência de IA** (Copilot Chat /
modelos de linguagem). Toda a metodologia — o que foi delegado, o que foi
revisado e como o output foi auditado — está descrita em
[AI_USAGE.md](AI_USAGE.md).

---

## Licença

Uso interno. Sem licença pública.
