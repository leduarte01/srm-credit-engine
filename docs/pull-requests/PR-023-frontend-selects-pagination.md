# PR #23 — Selects (produto + moeda BRL/USD) + paginação server-side

> GitHub PR: leduarte01/srm-credit-engine#21
> Melhorias do roadmap: M4 + M5 + M6.

## Summary

Endurece a UX do painel substituindo **três inputs livres** por selects
com domínio fechado, evitando inputs inválidos:

- **Produto** — `<select>` com os três produtos do catálogo
  mostrando os spreads como hint (`DUPLICATA 1.5% a.m.` etc.).
- **Moeda** — `<select>` BRL/USD no simulador e nos filtros da grid.
- **Paginação** — controles **Prev / Next + "Exibindo X–Y de Z"**
  tornando visível a paginação server-side já existente no
  `GET /receivables`.

## Scope

- `frontend/src/components/PricingSimulator.tsx` — selects.
- `frontend/src/components/ReceivableFilters.tsx` — select de moeda.
- `frontend/src/components/ReceivableTable.tsx` — controles de
  paginação + contador.
- `frontend/src/pages/DashboardPage.tsx` — state `page` controlado.

## Quality gates

- Vitest para componentes de filtro + paginação.
- Validação manual de borda (page=1, last page, vazia).
