# Critérios de Aceite — SRM Credit Engine v1.0.0

Este documento consolida os critérios de aceite verificáveis do
produto, organizados pelas quatro dimensões exigidas pelo case:
**usabilidade, segurança, desempenho e escalabilidade**. Cada critério
referencia o requisito do case que o origina e, quando aplicável, a
evidência no código ou na suíte de testes.

> **Como ler.** Cada critério tem três campos: **Dado / Quando /
> Então** (estilo Gherkin enxuto). Critérios marcados ✅ estão
> automatizados; ☑ são verificados manualmente; 🛈 são qualidades
> contínuas (monitoradas, não testáveis em um snapshot).

---

## 1. Usabilidade

### CA-U-01 — Operador precifica um recebível em até três interações
- **Dado** um operador autenticado no Painel do Operador.
- **Quando** preenche `face_value`, `issue_date`, `due_date`,
  `product_code` e dispara **Simular**.
- **Então** o `present_value` e o `settlement_value` aparecem em
  ≤ 500 ms (p95 em rede local) sem recarregar a página.
- **Evidência:** [PricingSimulator.tsx](frontend/src/components/PricingSimulator.tsx);
  endpoint `POST /api/v1/pricing/simulate`.
- **Status:** ✅ (vitest cobre o componente; latência medida em dev).

### CA-U-02 — Grid de transações sustenta filtragem incremental
- **Dado** um histórico com ≥ 1.000 recebíveis no banco.
- **Quando** o operador altera filtros (cedente, status, moeda,
  janela de datas).
- **Então** a tabela atualiza com **paginação server-side**
  (`offset`/`limit`) sem travar a UI; "Showing X of Y" reflete o
  total filtrado.
- **Evidência:** [ReceivableTable.tsx](frontend/src/components/ReceivableTable.tsx);
  endpoint `GET /api/v1/receivables` aceita `offset`, `limit` (default 50, máx 200).
- **Status:** ✅ backend; ☑ UX manual (controles prev/next a evoluir).

### CA-U-03 — Erros da API são mostrados de forma acionável
- **Dado** uma requisição que retorna `4xx` ou `5xx`.
- **Quando** o frontend recebe o envelope `{ code, message }`.
- **Então** a UI mostra a mensagem em tom de alerta, sem travar a
  app, e o usuário consegue corrigir o input e tentar novamente.
- **Evidência:** [client.ts](frontend/src/api/client.ts) — `ApiClientError`;
  [errors.py](backend/src/srm_credit_engine/api/v1/errors.py).
- **Status:** ✅ (vitest cobre `ApiClientError`).

### CA-U-04 — Documentação OpenAPI navegável
- **Dado** o backend em execução.
- **Quando** acesso `GET /docs`.
- **Então** vejo todos os endpoints, schemas Pydantic e exemplos
  prontos para invocação via Swagger UI.
- **Evidência:** FastAPI auto-expõe `/docs` e `/openapi.json`.
- **Status:** ✅.

---

## 2. Segurança

### CA-S-01 — Validação estrita de entrada
- **Dado** qualquer endpoint que aceite payload.
- **Quando** o cliente envia tipos incorretos, valores fora de
  range, datas inválidas, valores monetários não-string ou com
  precisão inadequada.
- **Então** a API responde `422` com lista de erros campo-a-campo,
  **sem expor stack trace**.
- **Evidência:** schemas Pydantic v2 em
  [schemas/](backend/src/srm_credit_engine/api/v1/schemas/);
  `validation_handler` global em
  [errors.py](backend/src/srm_credit_engine/api/v1/errors.py).
- **Status:** ✅ (`test_pricing_and_settlement.py` cobre 422s).

### CA-S-02 — Dinheiro como string decimal end-to-end
- **Dado** qualquer payload de API com campo monetário.
- **Quando** o valor trafega entre frontend, backend e banco.
- **Então** o tipo é **string decimal** (ex.: `"1234.56"`), nunca
  `float`/`number`; o banco usa `NUMERIC(38, 18)`; o frontend usa
  `decimal.js` no boundary.
- **Evidência:** [ADR-003](docs/adr/ADR-003-decimal-money.md);
  [money.py](backend/src/srm_credit_engine/domain/value_objects/money.py);
  [domain.ts](frontend/src/types/domain.ts).
- **Status:** ✅ (property-based tests via Hypothesis).

### CA-S-03 — Erros internos não vazam detalhes
- **Dado** uma exceção inesperada no backend.
- **Quando** o handler global captura.
- **Então** o cliente recebe `{ code: "internal_error", message: "..." }`
  com mensagem sanitizada; stack trace fica apenas nos logs
  estruturados (com `trace_id`).
- **Evidência:** [errors.py](backend/src/srm_credit_engine/api/v1/errors.py);
  [logging.py](backend/src/srm_credit_engine/observability/logging.py).
- **Status:** ✅ (`test_observability.py` valida `trace_id` em logs).

### CA-S-04 — Sem segredos no repositório
- **Dado** os arquivos versionados.
- **Quando** auditados.
- **Então** apenas `*.env.example` existem; nenhum `.env` ou
  segredo aparece em `git ls-files`; pre-commit `check-added-large-files`
  evita binários inesperados.
- **Evidência:** `.gitignore` cobre `.env`, `.venv`,
  `node_modules`, `__pycache__`, `.hypothesis`, `coverage`, `dist`,
  `build`.
- **Status:** ✅ (verificado em CI; pre-commit obrigatório).

### CA-S-05 — Concorrência de liquidação não corrompe estado
- **Dado** dois operadores tentando liquidar o **mesmo** recebível
  simultaneamente.
- **Quando** ambas as requisições chegam ao backend.
- **Então** apenas **uma** vence; a outra recebe
  `ConcurrencyConflictError` (HTTP 409) e a aplicação não persiste
  estado inconsistente.
- **Evidência:** coluna `version` em `ReceivableORM` e
  `SettlementORM` em
  [models.py](backend/src/srm_credit_engine/infrastructure/models.py);
  checagem em
  [repositories.py](backend/src/srm_credit_engine/infrastructure/repositories.py).
- **Status:** ✅ (testado em `test_repositories.py`).

---

## 3. Desempenho

### CA-P-01 — Latência de precificação simples
- **Critério:** `POST /api/v1/pricing/simulate` p95 ≤ **150 ms** em
  rede local com FX em cache.
- **Como medir:** prometheus exporter expõe
  `http_request_duration_seconds_bucket` por endpoint.
- **Status:** 🛈 monitorado em runtime.

### CA-P-02 — Listagem paginada de recebíveis
- **Critério:** `GET /api/v1/receivables?limit=50` p95 ≤ **300 ms**
  com até **100.000** registros no banco e filtros típicos
  (cedente + janela de datas).
- **Como medir:** query plan com `EXPLAIN ANALYZE`; índices em
  `(assignor_id, due_date)` e `(status, currency_code)` em
  [V1__init.sql](db/migrations/V1__init.sql).
- **Status:** 🛈 a validar em ambiente de carga.

### CA-P-03 — Relatórios analíticos via SQL nativo
- **Critério:** `GET /api/v1/reports/*` não usa o ORM puro;
  consultas são pré-escritas, parametrizadas e otimizadas para o
  plano do PostgreSQL.
- **Evidência:**
  [analytics_repository.py](backend/src/srm_credit_engine/infrastructure/analytics_repository.py)
  usa `sqlalchemy.text()` com queries explícitas em
  [queries.py](backend/src/srm_credit_engine/domain/analytics/queries.py).
- **Status:** ✅.

### CA-P-04 — Resiliência ao feed de câmbio
- **Critério:** indisponibilidade do provedor FX **não derruba**
  o sistema; resposta degradada usa a última taxa válida em cache
  ou retorna `503` com `code: fx_unavailable`.
- **Evidência:** stack cache(DB) → circuit breaker (purgatory) →
  retry (tenacity) em
  [resilience/](backend/src/srm_credit_engine/resilience/);
  [ADR-004](docs/adr/ADR-004-resilience-layering.md).
- **Status:** ✅ (`test_resilience.py` cobre todos os caminhos).

### CA-P-05 — Cobertura mínima de testes
- **Critério:** `pytest --cov` ≥ **80%** em cada PR; CI **falha**
  abaixo disso.
- **Evidência:** [backend.yml](.github/workflows/backend.yml).
- **Status:** ✅.

---

## 4. Escalabilidade

### CA-E-01 — Stack roda em containers idempotentes
- **Critério:** `docker compose up --build` parte do zero,
  aplica migrations automaticamente e expõe SPA + API + DB em < 90 s
  em hardware comum.
- **Evidência:** [docker-compose.yml](docker-compose.yml);
  [entrypoint.sh](backend/docker/entrypoint.sh) executa `alembic
  upgrade head`.
- **Status:** ✅.

### CA-E-02 — Arquitetura desacoplada (hexagonal)
- **Critério:** dependências apontam **sempre** da `infrastructure`
  para `domain`, nunca o contrário; trocar Postgres por outro store
  exige apenas adaptador novo, não mudança de regra.
- **Evidência:** [ADR-002](docs/adr/ADR-002-hexagonal-architecture.md);
  ports em
  [domain/ports/](backend/src/srm_credit_engine/domain/ports/).
- **Status:** ✅ (estrutura física do código garante).

### CA-E-03 — Domínio puro testável sem infra
- **Critério:** suíte unitária roda **sem** banco, sem rede e sem
  fixtures pesadas — `pytest -m "not integration"` < 5 s.
- **Evidência:** [tests/unit/](backend/tests/unit/) usa fakes em
  memória e Hypothesis para invariantes.
- **Status:** ✅.

### CA-E-04 — Roteiro de alta escala documentado
- **Critério:** o projeto descreve **como escalar** para
  ~1 milhão de transações/minuto (caching, sharding, read replicas,
  CQRS, fila, replicação cross-region) sem reescrita.
- **Evidência:**
  [docs/architecture/high-scale.md](docs/architecture/high-scale.md).
- **Status:** ✅ (proposta arquitetural com trade-offs).

### CA-E-05 — Proposta de EDA para integração futura
- **Critério:** evolução para arquitetura orientada a eventos é
  factível sem refazer o core — Transactional Outbox + catálogo de
  eventos descritos.
- **Evidência:**
  [docs/architecture/eda.md](docs/architecture/eda.md).
- **Status:** ✅ (proposta).

### CA-E-06 — Observabilidade nativa para diagnóstico em escala
- **Critério:** todo request gera log estruturado com `trace_id`;
  métricas Prometheus para latência, contadores de erro, throughput;
  spans OTel propagados.
- **Evidência:** [ADR-005](docs/adr/ADR-005-observability-stack.md);
  [observability/](backend/src/srm_credit_engine/observability/).
- **Status:** ✅.

---

## 5. Critérios fora de escopo de v1.0.0

Listados para evitar ambiguidade — **não** são aceitáveis para v1.0.0
mas estão no roadmap pós-release:

- Autenticação/autorização real (hoje a app assume operadores
  confiáveis; gate de identidade fica para v1.1).
- Multi-tenancy ativa com Row-Level Security (ADR-006 declara
  postura **single-tenant** atual).
- Pipeline de deploy contínuo para cloud (CI hoje só constrói
  imagens; push para registry e rollout são manuais).
- IaC (Terraform/Kubernetes manifests).
- Frontend com paginação por botões prev/next explícitos (UX a
  evoluir).

---

## 6. Como esses critérios são auditados

1. **Pre-commit + CI** garantem CA-S-01, CA-S-02, CA-S-04, CA-P-05
   em **todo PR**.
2. **Suíte de testes** (`backend/tests/`, `frontend/src/**/*.test.ts`)
   cobre os critérios marcados ✅.
3. **Runbooks** em
   [docs/architecture/runbooks/](docs/architecture/runbooks/) tratam
   degradações em produção quando algum critério é violado.
4. **Critérios 🛈** (qualidades contínuas) são monitorados via
   Prometheus + alertas — fora do escopo de teste unitário.
