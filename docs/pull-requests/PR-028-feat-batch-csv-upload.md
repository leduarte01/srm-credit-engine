# PR #28 — Upload em lote de recebíveis via CSV

> GitHub PR: leduarte01/srm-credit-engine#28
> Melhoria do roadmap: M8.

## Summary

Adiciona um **modal de upload em lote** (`BatchUploadModal`) com
drag-and-drop de arquivos `.csv`, parsing client-side, validação
**linha a linha** e relatório consolidado (sucessos / erros por
linha). Linhas válidas são enviadas via `POST /receivables` em
paralelo controlado (concorrência limitada); erros não bloqueiam o
restante do lote (criação parcial). Arquivo de exemplo em
[scripts/receivables_sample.csv](../../scripts/receivables_sample.csv).

Cabeçalho esperado do CSV:

```
assignor_document,product_code,face_value,currency,issue_date,due_date,external_reference
```

## Scope

- `frontend/src/components/BatchUploadModal.tsx` (novo) — UI + parsing
  - invocação em lote.
- `frontend/src/lib/csv.ts` (novo) — parser tipado com narrowing.
- `frontend/src/pages/DashboardPage.tsx` — botão de abertura.
- `scripts/receivables_sample.csv` — exemplo versionado.

## Quality gates

- Vitest cobrindo parser (header faltando, célula vazia, data
  inválida, sucesso total).
- Cast `Object.fromEntries` via `unknown` para passar `tsc strict`.
