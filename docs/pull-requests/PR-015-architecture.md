# PR #15 — Documentação de Arquitetura: ADRs + C4 + High-Scale + EDA + Runbooks

## Summary
Consolida a documentação arquitetural do **SRM Credit Engine** em
quatro frentes complementares: (1) cinco novos **ADRs** que tornam
imutáveis as decisões de arquitetura hexagonal, dinheiro como decimal
serializado em string, empilhamento de resiliência para câmbio, stack
de observabilidade (OTel + Prometheus + structlog) e postura de
multi-tenancy single-DB com `tenant_id`; (2) **três diagramas C4**
(Contexto, Containers, Componentes) em Mermaid que mostram do escopo
de sistema até a composição interna do backend hexagonal; (3) um
documento de **escalabilidade** que enumera, em ordem de aplicação,
os padrões (PgBouncer, read replicas, cache externo, particionamento,
queues, multi-region, CQRS) com as métricas-gatilho que justificam
cada degrau; (4) uma nota de **EDA** descrevendo o padrão Transactional
Outbox como caminho mínimo para integração orientada a eventos sem
abandonar o PostgreSQL como fonte da verdade; e (5) cinco **runbooks**
de crise (FX outage, DB outage, latency spike, migration failure,
suspeita de vazamento cross-tenant) com detecção, diagnóstico,
mitigação, recuperação e prevenção. Nenhuma mudança de código — apenas
documentação que torna a arquitetura existente legível, defensável e
operável.

## Scope
- `docs/adr/ADR-002-hexagonal-architecture.md` — registra o uso de
  Ports & Adapters com `domain/`, `api/v1/`, `infrastructure/` e
  `resilience/`, ancora a regra de dependência (domínio não importa
  nada de fora) e justifica a escolha contra arquitetura em camadas
  e Clean Architecture explícita.
- `docs/adr/ADR-003-decimal-money.md` — fixa `Decimal` no backend,
  string no JSON, `decimal.js` no frontend e `NUMERIC(20, 8)` em
  PostgreSQL como representação fim-a-fim para valores monetários,
  com `ROUND_HALF_EVEN` como regra de arredondamento.
- `docs/adr/ADR-004-resilience-layering.md` — define a composição
  `Cache(DB) → CircuitBreaker(purgatory) → Retry(tenacity) → HTTP`
  para o adaptador de câmbio, com parâmetros explícitos
  (3 tentativas, threshold 5, recovery 30s, TTL 3600s) e garantias
  de idempotência e observabilidade.
- `docs/adr/ADR-005-observability-stack.md` — adota OpenTelemetry
  (traces + métricas) + Prometheus exporter + structlog (JSON com
  `trace_id`), com convenções de atributos (semconv + prefixo `srm.`),
  buckets de histograma e probes `/health`, `/health/ready` e
  `/metrics`.
- `docs/adr/ADR-006-multi-tenancy.md` — declara o modelo single-DB
  compartilhado com `tenant_id` por linha, RLS como defense-in-depth,
  índices prefixados por `tenant_id` e teste de isolamento dedicado.
- `docs/adr/README.md` — índice de ADRs atualizado com as cinco novas
  entradas.
- `docs/architecture/README.md` — sumário do diretório e mapa para os
  documentos abaixo.
- `docs/architecture/c4-context.md` — diagrama C4 nível 1 em Mermaid
  com atores (Analista, Operações, Auditor) e sistemas externos
  (AwesomeAPI, backend de observabilidade).
- `docs/architecture/c4-containers.md` — diagrama C4 nível 2: SPA
  (Vite/nginx), API (FastAPI/Uvicorn), DB (PostgreSQL 16), com
  matriz de comunicação inter-container.
- `docs/architecture/c4-components.md` — diagrama C4 nível 3 do
  backend mostrando `domain/`, `api/v1/`, `infrastructure/`,
  `resilience/` e `observability/` com regras explícitas de
  dependência e o fluxo ponta-a-ponta de uma requisição de pricing.
- `docs/architecture/high-scale.md` — sete degraus de escala em ordem
  de aplicação (PgBouncer, read replicas, Redis, particionamento,
  queue, multi-region, CQRS), cada um amarrado a uma métrica-gatilho
  Prometheus e a sinais que precedem a decisão.
- `docs/architecture/eda.md` — Transactional Outbox como padrão: DDL
  da tabela `outbox`, sequência de publicação, catálogo proposto de
  eventos (`assignor.*`, `receivable.*`, `settlement.*`,
  `exchange_rate.*`), comparação Kafka/RabbitMQ/SNS, garantias
  (exactly-once em PG, at-least-once no bus) e roadmap incremental
  até o primeiro consumidor (read-model de analytics).
- `docs/architecture/runbooks/README.md` — índice de runbooks com
  severidades P0–P3, SLAs de resposta e princípios de gestão de crise
  (estabilizar antes de explicar; pós-mortem blameless).
- `docs/architecture/runbooks/fx-outage.md` — provedor de câmbio
  caído (P2): detecção via Prometheus, mitigação por extensão de TTL
  e flag `STRICT_FX_FRESHNESS`, recuperação automática via half-open
  do circuit breaker.
- `docs/architecture/runbooks/db-outage.md` — PostgreSQL inacessível
  (P0) com cenários A–D (saturação de conexões, disco cheio, failover
  da primária, migração travada) e ações concretas para cada.
- `docs/architecture/runbooks/latency-spike.md` — pico de p95 (P2/P1):
  árvore de decisão por rota, top-N queries via `pg_stat_statements`,
  ações tabeladas por causa raiz.
- `docs/architecture/runbooks/migration-failure.md` — migração alembic
  falhou (P1): classificação A–D (conflito de schema, constraint
  violada, deadlock, erro lógico) com receitas específicas por causa.
- `docs/architecture/runbooks/tenant-leak.md` — suspeita de vazamento
  cross-tenant (P0): isolar tenants envolvidos, verificar RLS via
  `pg_tables.rowsecurity`/`pg_policies`, conferir middleware de
  contexto e queries cruas, comunicação com compliance.
- `docs/COMMITS.md` — entrada da Etapa 13 adicionada e fix do Docker
  (README.md no builder) registrado na Etapa 12 retroativamente.

## Architectural notes
- Os ADRs são **imutáveis** após aceitos; mudanças geram novo ADR que
  marca o anterior como `Supersedes`. O índice mantém status visível.
- Toda decisão na seção de high-scale é precedida por **métrica
  Prometheus mensurável** — não há decisão antecipada sem dado.
- O padrão Outbox foi escolhido sobre publicação direta no broker
  porque preserva o PostgreSQL como fonte da verdade: o evento só
  sai depois do COMMIT, garantindo exactly-once relativo ao banco.
- Runbooks seguem a estrutura **Detecção → Diagnóstico → Mitigação →
  Recuperação → Pós-mortem**, sempre listando o que **não fazer** ao
  lado do que fazer.
- Diagramas C4 foram desenhados para Mermaid nativo do GitHub — sem
  dependência de ferramentas externas (PlantUML, Structurizr).

## Testing
- N/A — PR de documentação. CI dos workflows existentes
  (`backend.yml`, `frontend.yml`, `docker.yml`) não é afetado.
- Renderização Mermaid dos três C4 + sequência do outbox validada
  visualmente no preview do GitHub.

## Risks & Mitigations
- **Doc drift** — ADRs e runbooks podem desatualizar conforme o
  código evolui. Mitigação: revisão trimestral marcada no
  `docs/PLAN.md` (Etapa 14) e checklist de PR pedindo atualização
  quando a mudança afeta uma decisão registrada.
- **Excesso de documentação** — risco de KISS violado se o conteúdo
  virar enciclopédia. Mitigação: cada arquivo tem propósito
  declarado no topo do `architecture/README.md` e nenhuma decisão é
  registrada sem opção real avaliada.

## Out of Scope
- Implementação do outbox (descrita como roadmap em `eda.md`; será
  ADR futuro quando viermos a executar).
- Provisionamento real de PgBouncer/Redis/queue (também roadmap).
- Pós-mortems históricos: nenhum incidente real ocorreu ainda;
  template fica pronto para o primeiro evento.
