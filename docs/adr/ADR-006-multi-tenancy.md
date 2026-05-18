# ADR-006 — Postura de multi-tenancy: single-DB compartilhado com `tenant_id` por linha

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2026-04-12 | Engenharia |

## Contexto

O **SRM Credit Engine** opera para FIDCs (Fundos de Investimento em
Direitos Creditórios), em que cada fundo é um **tenant** com:

- Carteira de cedentes (assignors) e recebíveis exclusiva.
- Regras de pricing parametrizáveis por fundo.
- Requisito regulatório de **isolamento de dados** (CVM 175 / ANBIMA).

Multi-tenancy precisa equilibrar:

1. **Isolamento lógico forte** — vazamento cross-tenant é incidente
   crítico.
2. **Custo operacional baixo** — equipe pequena; migrações
   independentes por tenant não escalam.
3. **Onboarding rápido de tenant novo** — sem provisionar database.
4. **Performance previsível** — sem hotspot por tenant gigante.

## Opções avaliadas

### 1. Database por tenant

- 👍 Isolamento físico total.
- 👎 N migrações; backup N×; pool de conexões N×; onboarding lento.
- 👎 Inviável com equipe enxuta.

### 2. Schema por tenant (PostgreSQL `SET search_path`)

- 👍 Isolamento lógico forte; backup unificado.
- 👍 Modelo conhecido em SaaS B2B.
- 👎 Migração precisa varrer N schemas — risco operacional cresce
  linearmente.
- 👎 Pool de conexões precisa setar `search_path` por checkout — frágil.

### 3. **Tabela compartilhada com `tenant_id` por linha + RLS opcional** ✅

Toda tabela de domínio possui `tenant_id UUID NOT NULL`; queries
filtram por `tenant_id` extraído do contexto da requisição;
Row-Level Security (RLS) do PostgreSQL é ativada como _defense in
depth_.

- 👍 Migração única; backup único; pool único.
- 👍 Onboarding = criar linha em `tenant`. Sem DDL.
- 👍 RLS força isolamento no servidor — mesmo um bug na aplicação não
  vaza dados.
- 👎 Indexação por `(tenant_id, ...)` é obrigatória para evitar varredura
  cross-tenant.

## Decisão

> **Status atual (v1.0.0):** Arquitetura **single-tenant em produção**.
> O esquema versionado em [V1__init.sql](../../db/migrations/V1__init.sql)
> **ainda não inclui a coluna `tenant_id`** — a "preparação" descrita
> aqui é a **postura arquitetural** (ports/adapters desacoplados,
> repositórios isolados por interface, código sem lógica embutida que
> dificultaria a migração), não um schema fisicamente pronto. A
> introdução de `tenant_id` em todas as tabelas, dos índices compostos
> e da RLS será o **primeiro passo** do onboarding do segundo tenant e
> exigirá uma migração `alembic` dedicada + um ADR de seguimento.

### Princípios

1. **Tenant ID na borda** — middleware FastAPI extrai `tenant_id` do
   token JWT (futuro) ou cabeçalho `X-Tenant-Id` (interno) e injeta no
   contexto da requisição.
2. **Repositório aplica filtro automaticamente** — `ReceivableRepository`
   recebe `tenant_id` por DI; todo SELECT/UPDATE/DELETE inclui o
   predicado.
3. **Índices compostos prefixados com `tenant_id`** — `(tenant_id, ...)`
   em chave primária composta ou índice secundário.
4. **RLS como segunda linha de defesa** — `CREATE POLICY ...` por
   tabela; `SET app.tenant_id` por sessão; `FORCE ROW LEVEL SECURITY`
   habilitado em produção.
5. **Testes de isolamento** — suite dedicada que executa operações com
   dois `tenant_id` distintos e verifica que nenhum vê dado do outro.

### Anti-padrões proibidos

- ❌ Query sem `WHERE tenant_id = :tenant_id` em código de domínio.
- ❌ `OR tenant_id IS NULL` — todo dado tem tenant.
- ❌ Cache em memória por chave sem prefixo de tenant.

## Consequências

### Positivas

- Onboarding novo tenant = 1 insert + provisionar credencial.
- Operação simples (1 DB, 1 backup, 1 pipeline de migração).
- RLS converte bug de aplicação em erro 500, não em vazamento.

### Negativas (e mitigação)

- Tenant gigante pode criar hotspot — mitigado por particionamento
  PostgreSQL por `tenant_id` quando volume justificar (ADR futuro).
- Bug em filtro = vazamento — mitigado por RLS + testes dedicados.
- Backup seletivo de um tenant exige `pg_dump --table` com `WHERE` —
  documentado em runbook.

## Referências

- _Multi-Tenant Data Architecture_ — Microsoft Patterns & Practices.
- PostgreSQL Row-Level Security (docs oficiais).
- CVM 175 (FIDCs) — requisitos de segregação de dados.
