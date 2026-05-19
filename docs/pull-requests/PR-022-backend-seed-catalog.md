# PR #22 — Seed do catálogo (moedas + tipos de produto)

> GitHub PR: leduarte01/srm-credit-engine#19

## Summary

Adiciona migration Alembic que **popula o catálogo base** necessário
para o sistema funcionar out-of-the-box: moedas (`BRL`, `USD`) e tipos
de produto (`DUPLICATA`, `CHEQUE`, `CONTRATO_USD`) com códigos
alinhados às strategies registradas em
`PricingStrategyResolver`. Resolve o problema de `PricingSimulator`
falhar ao iniciar uma stack vazia.

## Scope

- `backend/alembic/versions/<hash>_seed_catalog.py` (nova migration
  idempotente — `INSERT ... ON CONFLICT DO NOTHING`).
- `backend/src/srm_credit_engine/domain/pricing/strategies/__init__.py` —
  códigos dos produtos validados contra o seed.

## Quality gates

- `alembic upgrade head` + `alembic downgrade -1` idempotente.
- Testes de integração da API passam com DB recém-criado.
