# PR #17 — Release v1.0.0 + hotfix protocol + QA fixes

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
princípios não-negociáveis, receita pedagógica explicitamente marcada
como **não aplicada** ao histórico, checklist pós-hotfix, anti-padrões
proibidos e protocolo de comunicação durante o incidente. Cria
`docs/acceptance-criteria.md` consolidando os critérios de aceite do
case (usabilidade, segurança, desempenho, escalabilidade) com 20+ regras
testáveis e suas evidências no código. Move `AI_USAGE.md` para a raiz
do repositório (conforme o case spec §2). Atualiza
`docs/adr/ADR-006-multi-tenancy.md` para deixar explícito que a coluna
`tenant_id` **ainda não** existe no schema v1. Adiciona descrição
retroativa do PR-004 (lint + lockfile + preservação do case spec).
Atualiza `docs/PLAN.md` marcando todas as etapas como completas e
registra a Etapa 15 em `docs/COMMITS.md`. **Sem código de produção
alterado** — apenas governança de release e documentação operacional.

## Scope
- `CHANGELOG.md` (raiz, novo) — Keep a Changelog 1.1.0 com entrada
  `[1.0.0] — 2026-05-18` agrupada por área (Backend, Frontend,
  Orquestração, CI/CD, Documentação, Versionamento) + seção de
  Quality Gates + Referências + rodapé com links de comparação.
- `docs/HOTFIX_PROTOCOL.md` (novo) — Quando usar (P0/P1), 5
  Princípios, Variantes A/B/C com comandos `git` executáveis,
  Worked example **pedagógico** com alerta visual de que **não foi
  executado** no repo, Checklist pós-hotfix, Anti-padrões
  proibidos, tabela de Comunicação durante o incidente.
- `docs/acceptance-criteria.md` (novo) — critérios de aceite
  consolidados do case spec §5.2, organizados em quatro grupos
  (usabilidade, segurança, desempenho, escalabilidade) com 20+
  regras Dado/Quando/Então testáveis, marcação ✅ / ☑ / 🛈 e
  evidência por arquivo/teste; inclui seção explícita de "fora de
  escopo para v1.0.0".
- `AI_USAGE.md` (movido para raiz) — conforme case spec §2;
  conteúdo inalterado.
- `docs/adr/ADR-006-multi-tenancy.md` — bloco "Status atual"
  reescrito para deixar explícito que `tenant_id` **não está** no
  schema versionado em `V1__init.sql`; preparação é arquitetural
  (ports/adapters desacoplados), não física.
- `docs/pull-requests/PR-004-lint-and-lockfile.md` (novo
  retroativo) — fecha trilha de auditoria do diretório.
- `docs/PLAN.md` — etapas 5 a 15 ✅ (roadmap concluído).
- `docs/COMMITS.md` — Etapa 15 registrada com todos os commits.
- `README.md` — links atualizados para `AI_USAGE.md` na raiz e para
  `docs/acceptance-criteria.md`; árvore do repositório
  re-renderizada.

## Architectural notes
- O `CHANGELOG.md` é **canônico**: substitui inspeção de PRs no
  GitHub como fonte oficial das mudanças. `[Unreleased]` acumula
  mudanças futuras.
- O `HOTFIX_PROTOCOL` **formaliza** o ADR-001 em receitas
  executáveis. As três variantes cobrem 100% dos cenários reais
  sem reintroduzir branches `release/*` ou `hotfix/*` de longa
  duração. O worked example é **explicitamente** marcado como
  pedagógico — para ver o protocolo aplicado de verdade, basta
  inspecionar tags `v1.0.1+` quando existirem.
- O documento de **critérios de aceite** atende §5.2 do case spec
  e amarra cada critério a uma evidência verificável; é o contrato
  testável entre o produto e a engenharia.
- O ADR-006 honesto evita **alucinação documental**: declarar
  preparação física que não existe seria propaganda; declarar a
  preparação como arquitetural (e nada mais) é auditável.
- `AI_USAGE.md` na raiz alinha com a leitura literal do case spec
  ("inclua um arquivo `AI_USAGE.md` no repositório").

## Testing
- N/A — PR de documentação e governança. Workflows existentes
  (`backend.yml`, `frontend.yml`, `docker.yml`) devem ficar verdes
  sem alteração.
- Pre-commit roda nos novos arquivos (EOL, trailing-whitespace,
  large files).
- Validação visual: tabelas, listas, blocos de código e links
  internos renderizam corretamente no preview do GitHub.

## Risks & Mitigations
- **CHANGELOG drift** — mudanças futuras podem não ser registradas.
  Mitigação: seção `[Unreleased]` existe como template; convenção
  de atualizar no mesmo PR da mudança.
- **HOTFIX_PROTOCOL envelhecer** se ADR-001 mudar. Mitigação: o
  protocolo referencia o ADR-001 explicitamente; mudança no ADR
  força revisão (encadeamento auditável).
- **Critérios de aceite virarem documento morto** — risco
  comum. Mitigação: critérios marcados ✅ estão amarrados a testes
  automatizados; mudança neles obriga atualizar o documento.
- **Worked example confundido com mudança real**. Mitigação:
  bloco de alerta visual no topo da seção + linguagem revisada
  ("receita pedagógica (não executada)").

## Out of Scope
- Tag anotada `v1.0.0` — criada **após** o merge deste PR via
  `git tag -a v1.0.0` + `git push origin v1.0.0`.
- Execução real de hotfix (futura tag `v1.0.1`) — fluxo separado
  pós-release.
- Implementação física de `tenant_id` no schema — ADR de
  seguimento + migração `alembic` dedicada.
- Automação de bump de versão (`release-please`/`semantic-release`).
- Push de imagens Docker para registry público.
