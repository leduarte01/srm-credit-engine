# PR #20 — Sidebar layout + KPI cards no dashboard

> GitHub PR: leduarte01/srm-credit-engine#17

## Summary

Substitui o layout single-column do dashboard por um **app shell** com
sidebar fixa (navegação por seção) e área principal scrollável.
Adiciona quatro **KPI status cards** no topo: receivables ativos,
volume liquidado, taxa média de spread, próximos vencimentos. KPIs
consumidos via TanStack Query a partir dos endpoints `/reports/*`.

## Scope

- `frontend/src/components/AppShell.tsx` (novo) — layout 2-coluna
  responsivo.
- `frontend/src/components/KpiCard.tsx` (novo) — card tipado.
- `frontend/src/pages/DashboardPage.tsx` — orquestra KPIs + grid.
- `frontend/src/lib/i18n.ts` — chaves de label dos KPIs.

## Quality gates

- `vitest run` verde; snapshot do `KpiCard`.
- `tsc --noEmit`, `eslint`, `prettier --check` ok.
