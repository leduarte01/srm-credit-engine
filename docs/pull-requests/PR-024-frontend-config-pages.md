# PR #24 — Páginas de configuração (Cedentes + Taxas de Câmbio)

> GitHub PR: leduarte01/srm-credit-engine#22
> Melhorias do roadmap: M2 + M3.

## Summary

Cria duas páginas de configuração faltantes no SPA:

- **Cedentes** (`/assignors`) — listar + criar (nome, documento, limite
  de crédito) consumindo `GET/POST /assignors`.
- **Taxas de Câmbio** (`/fx-rates`) — listar + criar par/taxa/validade
  consumindo `GET/POST /fx-rates`, com histórico em
  `/fx-rates/{base}/{quote}/history`.

Ambas usam TanStack Query (cache + invalidation) e formulários
acessíveis (labels, `aria-*`, validação inline).

## Scope

- `frontend/src/pages/AssignorsPage.tsx` (nova).
- `frontend/src/pages/ExchangeRatesPage.tsx` (nova).
- `frontend/src/components/AssignorForm.tsx`,
  `ExchangeRateForm.tsx` (novos).
- `frontend/src/lib/api.ts` — endpoints tipados adicionados.
- Rotas registradas no `AppShell`.

## Quality gates

- Vitest cobrindo o submit + invalidação de query.
