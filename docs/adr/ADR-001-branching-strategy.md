# ADR-001 — Branching Strategy: GitHub Flow

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2025-01-15 | Engenharia |

## Contexto

O **SRM Credit Engine** é uma aplicação SaaS web (FastAPI + React + PostgreSQL)
de domínio financeiro, com ciclo de release contínuo. A estratégia de
branching precisa sustentar simultaneamente:

- **Pipeline único de CI/CD** com gate de qualidade obrigatório (lint, type
  check, testes, build) antes de qualquer integração em produção.
- **Conventional Commits** e **Pull Requests descritivos** como instrumento
  de revisão e auditoria.
- **Histórico linear e rastreável**, legível como changelog
  (`git log --first-parent`).
- **Versionamento semântico** (`vMAJOR.MINOR.PATCH`) marcando releases
  diretamente na branch de produção.
- **Protocolo de hotfix** baseado em `git revert` e `git cherry-pick`, sem
  necessidade de backport entre múltiplas branches de longa duração.
- **Princípios KISS / SOLID / DRY** — toda complexidade adicional deve ser
  justificada por um problema concreto, não por convenção.

## Opções avaliadas

### 1. Git Flow (Vincent Driessen, 2010)

Duas branches de longa duração (`main` para produção e `develop` para
integração) e branches de apoio (`feature/*`, `release/*`, `hotfix/*`).

- 👍 Familiar em organizações com releases versionadas e janela de QA
  explícita.
- 👎 **Sobreposição com tags SemVer**: `main` ≡ "última tag estável", logo
  `develop` torna-se redundante quando releases são contínuas.
- 👎 **Backport obrigatório**: todo hotfix em `main` exige `cherry-pick`
  manual para `develop`, multiplicando esforço e gerando histórico em
  "garfo".
- 👎 Custo cognitivo desproporcional para o ciclo de release contínuo
  pretendido neste projeto.
- 👎 O próprio autor publicou [nota em 2020](https://nvie.com/posts/a-successful-git-branching-model/)
  declarando o modelo **inadequado para aplicações web em entrega contínua**.

### 2. Trunk Based Development

Uma única branch (`trunk`/`main`) com commits diretos ou branches efêmeras
(< 1 dia); features incompletas escondidas atrás de **feature flags**.

- 👍 Histórico extremamente linear; deploy contínuo nativo.
- 👍 Padrão consolidado em hyperscalers (Google, Facebook).
- 👎 **Pressupõe infraestrutura de feature flags madura** (toggles
  persistentes, dashboard de rollout, kill switches) — fora do escopo
  desta solução.
- 👎 Branches efêmeras com merge antes do código estar funcionalmente
  completo enfraquecem a unidade de revisão (PR) como artefato de
  auditoria.
- 👎 A disciplina exigida (commits diários, testes < 5 min, flags em todo
  código incompleto) só compensa em times com plataforma de delivery
  amadurecida.

### 3. GitHub Flow (✅ escolhido)

Uma única branch protegida (`main`) sempre deployável; toda mudança nasce em
uma branch curta (`feat/*`, `fix/*`, `chore/*`, `docs/*`, `hotfix/*`), passa
por **Pull Request** com CI verde e revisão, e é mergeada via `--no-ff` para
preservar o ponto de integração.

- 👍 **Aderência natural a CI/CD** com pipeline único: cada PR roda o gate
  completo; `main` permanece sempre deployável.
- 👍 **Histórico linear** em `main` com merges `--no-ff` rotulando cada PR,
  facilitando leitura por `git log --first-parent` e geração de release
  notes.
- 👍 **PRs como unidade de auditoria**: cada mudança em produção tem um PR
  associado, com descrição, checklist e rastro de revisão.
- 👍 **Hotfix trivial**: branch `hotfix/*` de `main` → PR → tag patch.
  `git revert` e `cherry-pick` operam diretamente em `main`, sem backport.
- 👍 **Tags SemVer** marcam releases em `main` sem branch intermediária.
- 👍 **KISS**: uma única branch de longa duração contra as duas de Git Flow.
- 👍 Padrão adotado por **GitHub, Shopify, Basecamp, Stripe, Nubank, Stone**
  e referenciado em *Continuous Delivery* (Humble & Farley).
- 👎 Exige disciplina: sem branch protection, qualquer push direto quebra o
  modelo. **Mitigação:** branch protection rule documentada abaixo.

## Decisão

**Adotar GitHub Flow.**

### Regras operacionais

1. **`main`** é a única branch de longa duração e está sempre deployável.
2. Toda mudança nasce em branch curta, com prefixo semântico:
   - `feat/<slug>` — nova funcionalidade
   - `fix/<slug>` — correção de bug
   - `chore/<slug>` — manutenção, build, dependências
   - `docs/<slug>` — documentação
   - `hotfix/<slug>` — correção urgente em produção
3. **Conventional Commits 1.0.0** obrigatórios em toda mensagem.
4. **Pull Request** com descrição completa (template em
   [docs/pull-requests/](../pull-requests/)), checklist e CI verde antes
   do merge.
5. **Merge `--no-ff`** preserva o commit de merge como ponto de fechamento
   do PR, garantindo rastreabilidade via `git log --first-parent`.
6. **Rebase interativo** local antes do PR para limpar fix-ups e reordenar
   commits, mantendo cada commit autocontido e revisável.
7. **Tags SemVer** (`vMAJOR.MINOR.PATCH`) em `main` ao final de cada
   release.
8. **Release notes** geradas a partir dos Conventional Commits.

### Branch protection rules

Aplicar via UI do GitHub em `main`:

- Require pull request before merging.
- Require status checks to pass (CI: ruff + mypy + pytest + build).
- Require linear history.
- Disallow force-push e deleção.
- Restringir push direto (somente merge via PR).

### Gestão de crise

- **`git revert <sha>`** numa branch `hotfix/revert-<slug>` → PR → tag
  patch. Caminho padrão para desfazer um deploy ruim sem reescrever
  histórico.
- **`git cherry-pick <sha>`** quando um fix precisa ser aplicado a uma
  release branch efêmera (cenário raro, apenas sob exigência regulatória).
- **`release/vX.Y.Z` efêmera**, criada sob demanda quando uma versão
  precisa ser congelada para auditoria; recebe apenas fixes da release e é
  deletada após a tag.

## Consequências

### Positivas

- Histórico **linear, narrativo e auditável**.
- Pipeline de CI único e simples de manter.
- Custo cognitivo mínimo para revisores e novos contribuidores.
- Protocolo de hotfix sem backport.

### Negativas e mitigações

- **Sem branch de homologação permanente** → mitigado por:
  - CI completo gated em cada PR.
  - Ambiente de **staging** deployado a cada merge em `main` via Docker
    Compose.
  - **Release branches efêmeras** criadas sob demanda quando houver
    necessidade de congelamento para auditoria.
- **Disciplina PR-only** → mitigada por branch protection rule.

## Referências

- Driessen, V. — *A successful Git branching model* (2010, nota de 2020).
- Chacon, S. — *GitHub Flow* (<https://githubflow.github.io/>).
- Humble, J. & Farley, D. — *Continuous Delivery* (2010).
- Skelton, M. & Pais, M. — *Team Topologies* (2019).
- *Trunk Based Development* — <https://trunkbaseddevelopment.com/>.
