# PR #25 — Modal "Novo Recebível" + botão "Liquidar" inline

> GitHub PR: leduarte01/srm-credit-engine#23
> Melhoria do roadmap: M1.

## Summary

Operacionaliza o fluxo end-to-end de criação de recebível pela UI.
Adiciona um modal completo com todos os campos exigidos pelo
`POST /receivables` (assignor, produto, valor de face, moeda, datas,
referência externa) e validação client-side antes do submit. Cada
linha da grid ganha um botão **"Liquidar"** que dispara
`POST /settlements` com confirmação inline.

## Scope

- `frontend/src/components/NewReceivableModal.tsx` (novo).
- `frontend/src/components/ReceivableTable.tsx` — coluna de ações.
- `frontend/src/lib/api.ts` — `createReceivable`, `settleReceivable`.

## Quality gates

- Vitest cobrindo abrir modal → submit válido → invalidação.
- Tratamento de erro tipado via `ApiClientError`.
