# PR #29 — Revisão end-to-end pós-v1.0.0

> GitHub PR: leduarte01/srm-credit-engine#29

## Summary

Revisão completa da documentação após o ciclo de melhorias M1–M8
(PRs #18–#28). Sem mudanças de código de produção.

- **Auditoria de código morto** — varredura em `backend/src/` e
  `frontend/src/` confirma zero arquivos órfãos e zero exports não
  importados.
- **README** atualizado: tabela de endpoints corrigida
  (`/pricing/simulate`, `/fx-rates/{base}/{quote}/history`), nova
  seção **"Funcionalidades de produto"**, nova seção
  **"Hospedagem"** documentando EasyPanel + secrets + rollback,
  seção **"Qualidade, CI e CD"** documentando o webhook de deploy.
- **AI_USAGE.md** com adendo pós-v1.0.0 documentando três
  alucinações observadas e suas mitigações (AwesomeAPI rate-limit,
  exceções não tratadas, tipos `dict` sem parâmetros).
- **PLAN.md** com M1–M8 marcadas como ✅ + referências aos PRs e
  link quebrado do ADR-001 corrigido.
- **CHANGELOG.md** promovido para `[1.1.0] — 2026-05-19` agrupando
  todas as mudanças pós-v1.0.0.
- **docs/COMMITS.md** com Etapas 16–20 cobrindo PRs #18–#29.
- **docs/pull-requests/** com 12 novos arquivos (`PR-018` a
  `PR-029`).

## Quality gates

- `prettier --write` aplicado a todos os docs.
- Sem mudanças de código → CI roda apenas os hooks de doc.
