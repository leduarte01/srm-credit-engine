# PR #26 — Cotação FX em tempo real (toggle + fallback DB→live)

> GitHub PR: leduarte01/srm-credit-engine#24
> Melhoria do roadmap: M7.

## Summary

Adiciona a capacidade de precificar usando cotação **ao vivo** em vez
da taxa cadastrada no banco, mantendo retrocompatibilidade total. O
backend introduz `LiveRateCurrencyConverter` (provedor externo) e
`FallbackCurrencyConverter` (DB → live em caso de
`ExchangeRateNotFoundError`), expostos via novo campo
`use_live_rate: bool` em `POST /pricing/simulate`. A resposta passa a
incluir `fx_rate_source: "database" | "live" | null` para auditoria.

O frontend ganha um **toggle** no `PricingSimulator` ("Usar cotação em
tempo real") e renderiza um **badge colorido** indicando a fonte da
taxa retornada.

## Scope

- `backend/src/srm_credit_engine/infrastructure/live_rate_converter.py`
  (novo).
- `backend/src/srm_credit_engine/infrastructure/fallback_currency_converter.py`
  (novo) — expõe `last_source`.
- `backend/src/srm_credit_engine/api/v1/routers/pricing.py` —
  constrói o converter por requisição com base em `use_live_rate`.
- `backend/src/srm_credit_engine/api/v1/schemas/pricing.py` — campos
  novos.
- `frontend/src/components/PricingSimulator.tsx` — toggle + badge.
- `frontend/src/types/domain.ts` — `use_live_rate?` + `fx_rate_source`.
- `frontend/src/lib/i18n.ts` — chaves `sim_use_live_rate`,
  `sim_fx_source_live`, `sim_fx_source_database`.

## Quality gates

- Unit tests cobrindo `FallbackCurrencyConverter` (caminhos DB ok / DB
  miss → live ok / ambos falham).
- Validação manual no painel.
