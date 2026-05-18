# PR #17 — Release v1.0.0 + hotfix protocol

## Summary
Fecha o roadmap do projeto com a entrega da primeira release oficial.
Introduz o `CHANGELOG.md` na raiz no formato **Keep a Changelog 1.1.0**
com a entrada agrupada `[1.0.0] — 2026-05-18` consolidando todo o
trabalho dos PRs #1 a #16 (backend Python 3.12 + FastAPI, frontend
React 19 + Tailwind v4, stack docker-compose, três workflows de CI,
seis ADRs + C4 + high-scale + EDA + runbooks, README + AI_USAGE).
Adiciona `docs/HOTFIX_PROTOCOL.md` formalizando — como decorrência
operacional do **ADR-001 (GitHub Flow + SemVer)** — três variantes
executáveis de hotfix (A: PR direto, B: revert via PR, C: cherry-pick),
princípios não-negociáveis (tag SemVer obrigatória, sem
branch-de-longa-duração, `git revert` precede `git cherry-pick`,
`main` sempre deployável), um **worked example** com cenário fictício
realista de recuperação de cobertura, checklist pós-hotfix,
anti-padrões proibidos e protocolo de comunicação durante o incidente.
Atualiza `docs/PLAN.md` marcando todas as etapas 5–15 como completas e
registra a Etapa 15 em `docs/COMMITS.md`. **Sem código de produção
alterado** — apenas governança de release e documentação operacional.

## Scope
- `CHANGELOG.md` (raiz, novo) — formato Keep a Changelog 1.1.0:
  - Seção `[Unreleased]` vazia (template para mudanças futuras).
  - Seção `[1.0.0] — 2026-05-18 — Added` agrupada por área:
    - **Backend** (FastAPI app, domínio hexagonal, Strategy de
      pricing, repositórios SQLAlchemy 2.0 async + Alembic,
      Currency Engine com cache→breaker→retry, structlog +
      OTel + Prometheus, exception handler global,
      `ApiClientError` envelope, decimal-string monetário).
    - **Frontend** (Painel do Operador, Grid de Transações com
      TanStack Table, TanStack Query + axios, decimal.js no
      boundary, Zustand 5, Tailwind v4 inline).
    - **Orquestração e operação** (docker-compose com 4 serviços,
      multi-stage images backend/frontend/nginx, healthchecks,
      volumes nomeados).
    - **CI/CD** (workflows `backend.yml`, `frontend.yml`,
      `docker.yml` com path filters; pre-commit; ruff/mypy
      strict/pytest cov ≥ 80%; prettier/eslint/tsc/vitest/vite
      build; docker/build-push-action@v6 + GHA cache).
    - **Documentação** (6 ADRs imutáveis, C4 contexto/container/
      componente, high-scale, EDA, 5 runbooks, README final,
      AI_USAGE).
    - **Versionamento** (tag anotada `v1.0.0`).
  - Seção `### Quality gates atendidos` (cobertura, mypy strict,
    pre-commit, CI verde).
  - Seção `### Referências` (links para ADRs, runbooks e PLAN).
  - Rodapé com links de comparação:
    `[Unreleased]: .../compare/v1.0.0...HEAD` e
    `[1.0.0]: .../releases/tag/v1.0.0`.
- `docs/HOTFIX_PROTOCOL.md` (novo) — protocolo operacional:
  - **Quando usar** (P0/P1, ≤ 100 linhas, ≤ 3 arquivos típicos).
  - **Princípios** (5: `main` sempre deployável, tag SemVer
    obrigatória, sem branch-de-longa-duração, `git revert` precede
    `git cherry-pick`, tudo documentado).
  - **Variantes** A (hotfix simples via PR), B (revert via PR
    quando commit ruim já está em `main`), C (cherry-pick quando
    fix já existe em outra branch) — cada uma com comandos `git`
    executáveis completos.
  - **Worked example** simulado: cenário fictício de "cobertura
    quebrada após remoção de teste" com tag `v1.0.0 → v1.0.1`,
    comandos do checkout até o `git push origin v1.0.1`.
  - **Checklist pós-hotfix** (tag, CHANGELOG, pós-mortem, teste de
    regressão, métrica/alerta, follow-up para branches longas).
  - **Anti-padrões proibidos** (tag sem PR, force-push, rebase em
    commit mergeado, `--no-verify`, hotfix sem teste).
  - **Comunicação durante o incidente** (tabela momento × canal ×
    conteúdo: início, PR aberto, merge, deploy, pós-mortem).
- `docs/PLAN.md` — etapas 5 a 15 marcadas como ✅ na tabela de
  status (todas as etapas do roadmap concluídas).
- `docs/COMMITS.md` — registra a Etapa 15.

## Architectural notes
- O `CHANGELOG.md` é **canônico**: substitui o ato de inspecionar
  PRs no GitHub como fonte oficial das mudanças. Entradas futuras
  acumulam em `[Unreleased]` e são promovidas para uma seção
  versionada a cada release — fluxo recomendado pelo Keep a
  Changelog.
- O `HOTFIX_PROTOCOL` **formaliza** o que o ADR-001 deixou em
  princípios: as três variantes (A/B/C) cobrem 100% dos cenários
  realistas sem precisar reintroduzir branches `release/*` ou
  `hotfix/*` de longa duração — a única branch criada vive o
  tempo da correção e some no merge.
- A simulação no worked example é **realista mas inofensiva**: usa
  um cenário fictício (cobertura quebrada) em vez de tocar em
  código de produção real, preservando a tag `v1.0.0` como release
  limpa enquanto demonstra `git revert`/`cherry-pick`.
- A entrada `[1.0.0]` agrupa por **área funcional** em vez de
  cronologicamente — facilita auditoria ("o que tem de
  observabilidade?") e revisão arquitetural sem precisar reler 16
  PRs.
- Todos os links no CHANGELOG e no HOTFIX_PROTOCOL são internos
  (paths relativos) ou apontam para documentação oficial pública —
  nenhuma URL é gerada/inventada.

## Testing
- N/A — PR de documentação e governança de release. Workflows
  existentes (`backend.yml`, `frontend.yml`, `docker.yml`) devem
  ficar verdes sem alteração.
- Pre-commit roda nos novos arquivos (hooks de hygiene: EOL,
  trailing-whitespace, large files).
- Validação visual: tabelas, listas, blocos de código e links
  internos do `CHANGELOG.md` e `HOTFIX_PROTOCOL.md` renderizam
  corretamente no preview do GitHub.

## Risks & Mitigations
- **CHANGELOG drift** — em releases futuras, mudanças podem ser
  esquecidas de registrar. Mitigação: seção `[Unreleased]` existe
  desde já como template; convenção (a ser reforçada em revisões)
  de atualizar `[Unreleased]` no mesmo PR da mudança.
- **HOTFIX_PROTOCOL pode envelhecer** se a branching strategy do
  ADR-001 mudar. Mitigação: o protocolo referencia o ADR-001
  explicitamente; qualquer mudança no ADR força revisão do
  protocolo (encadeamento auditável).
- **Worked example pode ser confundido com mudança real** —
  alguém lendo a história git pode buscar o cenário descrito.
  Mitigação: o documento marca explicitamente o cenário como
  "fictício realista usado como demonstração", e nenhum commit é
  efetivamente criado pelo exemplo.

## Out of Scope
- Tag anotada `v1.0.0` em si — será criada **após o merge** deste
  PR em `main`, com `git tag -a v1.0.0` + `git push origin v1.0.0`
  (comandos fornecidos ao operador no encerramento da etapa).
- Execução real de um hotfix — o protocolo descreve e demonstra;
  a execução só ocorre se um incidente real surgir.
- Automação de bump de versão (ferramenta tipo `release-please` ou
  `semantic-release`) — fica como possível follow-up; por ora a
  release é manual e auditável.
- Publicação de imagens Docker com a tag SemVer em um registry
  público — out of scope deste PR; o workflow `docker.yml` faz
  build mas não push para registry externo.
