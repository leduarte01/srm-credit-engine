# PR #21 — i18n PT/EN + help modal

> GitHub PRs: leduarte01/srm-credit-engine#18 + #20

## Summary

Adiciona suporte a **dois idiomas** (PT-BR padrão, EN secundário) com
toggle persistente em `localStorage` via Zustand. Todas as strings de
UI passam por `frontend/src/lib/i18n.ts` (objeto `messages` com chave
por idioma). Inclui um **modal contextual de ajuda** explicando a
fórmula de precificação, os três produtos com spreads, e o fluxo de
liquidação. Correção: `defaultProductCode` no `PricingSimulator` agora
bate com o catálogo de strategies do backend.

## Scope

- `frontend/src/lib/i18n.ts` — dicionários PT/EN.
- `frontend/src/store/uiStore.ts` — campo `locale` com persistência.
- `frontend/src/components/LanguageToggle.tsx` (novo).
- `frontend/src/components/HelpModal.tsx` (novo) — conteúdo
  educacional sobre spreads + fórmula.
- `frontend/src/components/PricingSimulator.tsx` — `defaultProductCode`
  corrigido + chaves i18n aplicadas.

## Quality gates

- Snapshot dos textos em PT e EN.
- Persistência do locale validada manualmente.
