# Escala — sobrevivendo a 10× e 100× a carga atual

Este documento descreve **gargalos previstos** e os **mecanismos de
evolução** para sustentar crescimento sem reescrita arquitetural.

A arquitetura atual (FastAPI + PostgreSQL + cache em DB para câmbio)
foi desenhada para volume **baixo a médio** (single-tenant, < 100 RPS
sustentados, < 1M recebíveis em base). Esta nota lista o que muda em
cada degrau de carga.

## Cenários de carga

| Cenário                   | Volume aproximado                              | Gargalo previsto                     |
| ------------------------- | ---------------------------------------------- | ------------------------------------ |
| **Atual**                 | < 100 RPS, < 1M recebíveis                     | Nenhum.                              |
| **10× (médio)**           | ~1k RPS, ~10M recebíveis, 10 tenants           | Conexões DB, hot paths de pricing.   |
| **100× (alto)**           | ~10k RPS, ~100M recebíveis, 50+ tenants        | Write throughput, latência cross-AZ. |
| **1000× (massivo)**       | > 10k RPS, > 1B recebíveis                     | Schema; reescrita orientada a eventos. |

## Padrões de escala (em ordem de aplicação)

### 1. Connection pooling externo (PgBouncer)

**Problema:** PostgreSQL custa ~10MB/conexão. SQLAlchemy + asyncpg
abrem N conexões por worker; com 10 réplicas × 4 workers × 20 conexões
= 800 conexões → satura o DB.

**Solução:** **PgBouncer em modo `transaction`** entre app e DB.
Reduz para conexões físicas ≈ número de CPUs do DB.

**Quando aplicar:** > 200 conexões físicas previstas. Custo:
1 sidecar / 1 ALB target.

**Cuidados:** `prepared statements` precisam ser desabilitados
ou usar `statement_cache_size=0` no asyncpg.

### 2. Read replicas + roteamento de queries

**Problema:** Reports e analytics fazem `SELECT` pesado em janela
agregada — competem com escritas de pricing.

**Solução:** **PostgreSQL streaming replication** para 1+ réplicas.
SQLAlchemy roteia leituras de _reports_ para o pool secundário; escritas
e leituras transacionais ficam no primário.

**Implementação:** dois `AsyncEngine` no `deps.py`
(`engine_rw`, `engine_ro`); flag `read_only=True` em métodos de
repositório de analytics.

**Quando aplicar:** queries de relatório > 10% do tempo do DB primário.

### 3. Cache externo (Redis) para leituras frequentes

**Problema:** Lista de tipos de produto, taxas administrativas e dados
de cedente são lidos a cada pricing — leitura repetida em PostgreSQL.

**Solução:** **Redis** com TTL para dados quase-imutáveis. Padrão
cache-aside; invalidação por evento em escrita.

**Implementação:** novo adaptador `CachedReceivableRepository`
empilhado no Composition Root, análogo ao padrão de câmbio.

**Quando aplicar:** > 30% do tempo de pricing em leituras repetidas.

### 4. Particionamento de tabelas por `tenant_id` ou data

**Problema:** Tabela `receivable` cresce milhões de linhas; índices
incham; vacuum fica lento; queries cross-tenant degradam.

**Solução:** **PARTITION BY HASH (tenant_id)** ou **PARTITION BY RANGE
(due_date)**. PostgreSQL 16 suporta partition pruning automático.

**Quando aplicar:** > 50M linhas em uma tabela _hot_.

**Custos:** migração com `pg_partman` ou rebuild offline.

### 5. Queue para offload assíncrono

**Problema:** Pricing em lote (1000 recebíveis) toma > 30s; HTTP timeouts
e degrada usuário.

**Solução:** **Job queue** (Celery + Redis ou Arq + Redis ou
RQ). Endpoint enfileira e retorna `job_id`; SPA faz polling em
`/api/v1/jobs/{id}`.

**Quando aplicar:** P95 de batch > 5s.

### 6. Replicação cross-region / multi-master

**Problema:** Tenant em outra região vê latência inaceitável.

**Solução:** **Logical replication** com filtro por `tenant_id`; ou
adoção de **CockroachDB** / **Yugabyte** para Postgres-compatible
multi-region. Pricing pode ser local; settlement permanece
single-master por requisito regulatório.

**Quando aplicar:** SLA < 200ms em > 1 região.

### 7. CQRS + leitura otimizada

**Problema:** Modelo relacional satura em joins complexos para analytics
em grande volume.

**Solução:** **Materialized views** ou **read model dedicado**
(ElasticSearch / ClickHouse) alimentado pelo outbox (ver
[EDA](eda.md)).

**Quando aplicar:** queries de relatório > P95 1s.

## Anti-padrões evitados

- **N+1 em ORM** — repositórios usam `selectinload`/`joinedload`
  explícitos; testes unitários conferem contagem de queries.
- **Sequential scans em tabelas grandes** — todo índice tem prefixo
  `(tenant_id, ...)`.
- **Locks longos** — transações curtas; sem `SELECT ... FOR UPDATE`
  sem timeout.
- **JSON em coluna `TEXT` sem GIN** — usar `JSONB` + GIN quando
  pesquisar interior.

## Métricas que precedem cada decisão

| Decisão                  | Métrica gatilho                                                |
| ------------------------ | -------------------------------------------------------------- |
| PgBouncer                | `pg_stat_database.numbackends` > 80% `max_connections`         |
| Read replica             | `pg_stat_database.tup_fetched` em leituras > 60% do total      |
| Redis cache              | hit-ratio < 5% em lookup de catálogo + `latency_p95` afetado   |
| Particionamento          | tabela > 50M linhas + `pg_stat_user_tables.n_dead_tup` cresce  |
| Queue                    | `srm_pricing_duration_seconds_bucket{le="5"}` P95 > 5s         |
| Multi-region             | latência inter-AZ > 50ms sustentada                            |

Toda decisão de escala é precedida por **medição** e registrada em um
**ADR**.
