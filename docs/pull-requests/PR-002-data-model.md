# PR #2 — Modelagem de dados (ER + DDL)

**Branch:** `feat/data-model` → `main`
**Tipo:** feat / docs

## O que foi feito
- Diagrama ER em Mermaid: `docs/ER.md`
- Script DDL completo PostgreSQL 16: `db/migrations/V1__init.sql`
  - Tabelas: `currency`, `exchange_rate`, `product_type`, `assignor`, `receivable`, `settlement`, `settlement_event`
  - Constraints: CHECK, FK, UNIQUE
  - Índices para queries analíticas
  - Seed: moedas BRL/USD, produtos (Duplicata 1.5%, Cheque 2.5%, Contrato USD 1.2%), taxa de câmbio inicial
  - Coluna `version` para **Optimistic Locking** em `receivable` e `settlement`
  - Coluna temporal `valid_from`/`valid_to` em `exchange_rate` (histórico)
  - Trilha de auditoria em `settlement_event` (jsonb)

## Decisões
- `NUMERIC` com precisão explícita (`20,4` valores, `9,6` taxas, `20,10` câmbio) — evita float
- `UUID` para entidades transacionais (preparação para sharding/replicação)
- `JSONB` para payload de auditoria — flexível para evolução EDA
- `gen_random_uuid()` via `pgcrypto`

## Checklist
- [x] Diagrama ER mostra relacionamentos Moeda × Produto × Transação × Taxa
- [x] DDL versionável (formato Flyway/Alembic-compatible)
- [x] Integridade referencial em todas as FKs
