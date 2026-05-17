# ADR-001 — Branching Strategy: GitHub Flow

| Status | Data       | Decisor        |
| ------ | ---------- | -------------- |
| Aceito | 2025-01-15 | Tech Lead (eu) |

## Contexto

O case técnico do **SRM Credit Engine** é uma aplicação SaaS web (FastAPI +
React + PostgreSQL) entregue como repositório público em prazo de 3 a 4 dias
úteis. O case (nível 🟣 Especialista) exige explicitamente que a estratégia
de branching seja **definida e justificada** no repositório, escolhendo entre
**Git Flow**, **Trunk Based Development** ou **GitHub Flow**.

A escolha precisa atender, simultaneamente:

- **CI/CD com pipeline único** (entregável sênior obrigatório).
- **Commits atômicos + Conventional Commits + PRs descritivos** (Pleno).
- **Histórico limpo, linear e rastreável** (critério 3 de avaliação).
- **Tags SemVer** marcando releases (`v1.0.0`).
- **Simulação de gestão de crise** com `git revert` ou `cherry-pick` (🟣).
- **Princípios SOLID / KISS / DRY** (critério 2 de avaliação) — overengineering
  é sinal negativo numa entrevista sênior.

## Opções avaliadas

### 1. Git Flow (Vincent Driessen, 2010)

Branches de longa duração: `main` (produção) e `develop` (integração); branches
de apoio: `feature/*`, `release/*`, `hotfix/*`.

- 👍 Familiar para times bancários legados; janela de QA explícita.
- 👎 **Sobreposição com tags SemVer** torna a duplicidade de "estado pronto
  para release" redundante (`main` ≡ última tag).
- 👎 Hotfix exige **backport** para `develop`, multiplicando o esforço de
  cherry-pick e gerando histórico em "garfo".
- 👎 Custo alto para uma equipe de 1 pessoa em ciclo de 4 dias.
- 👎 O próprio autor [declarou em 2020](https://nvie.com/posts/a-successful-git-branching-model/)
  que o modelo **não é apropriado para web apps em entrega contínua**.

### 2. Trunk Based Development

Uma única branch (`trunk`/`main`) com commits diretos ou branches **muito
curtas** (< 1 dia); features incompletas escondidas atrás de **feature flags**.

- 👍 Histórico extremamente linear; deploy contínuo nativo.
- 👍 Padrão em hyperscalers (Google, Facebook).
- 👎 **Pressupõe feature flags maduras** e infra de toggles (não há no escopo).
- 👎 Branches efêmeras dificultam a rastreabilidade dos PRs simulados
  exigidos no case (Pleno).
- 👎 Para um avaliador externo ler o histórico, "tudo em main" sem PRs
  intermediários enfraquece a narrativa de "o histórico conta uma história".

### 3. GitHub Flow (✅ escolhido)

Uma única branch protegida (`main`) sempre deployável; toda mudança nasce em
uma **branch curta** (`feat/*`, `fix/*`, `chore/*`, `hotfix/*`), passa por
**Pull Request** com CI verde e revisão, e é mergeada via `--no-ff` para
preservar o ponto de integração.

- 👍 **Aderência a CI/CD** com pipeline único — alinhado ao entregável sênior.
- 👍 **Histórico linear** em `main` com merges `--no-ff` rotulando cada PR,
  facilitando `git log --first-parent`.
- 👍 **PRs simulados** (Pleno) ficam visíveis: branch viva → PR descritivo →
  merge.
- 👍 **Hotfix trivial**: branch `hotfix/*` de `main` → PR → tag patch.
  `git revert` ou `cherry-pick` operam diretamente em `main` sem backport.
- 👍 **Tags SemVer** marcam releases em `main` sem branch intermediária.
- 👍 **KISS**: 1 branch de longa duração contra as 2 de Git Flow.
- 👍 Padrão adotado por **GitHub, Shopify, Basecamp, Stripe, Nubank, Stone**.
- 👎 Exige disciplina: não merge sem CI verde; sem branch protection vira
  caos. Mitigação: **branch protection rule** documentada abaixo.

## Decisão

**Adotar GitHub Flow.**

### Regras operacionais

1. **`main`** é a única branch de longa duração, sempre deployável.
2. Toda mudança nasce em branch curta — convenção de prefixos:
   - `feat/<slug>` — nova funcionalidade
   - `fix/<slug>` — correção
   - `chore/<slug>` — manutenção, build, deps
   - `docs/<slug>` — documentação
   - `hotfix/<slug>` — correção urgente em produção
3. **Conventional Commits 1.0.0** obrigatórios.
4. **Pull Request** com descrição rica (template em `docs/pull-requests/`),
   pelo menos 1 reviewer (em time real), CI verde.
5. **Merge `--no-ff`** preserva o commit de merge como ponto de fechamento
   do PR (rastreabilidade `git log --first-parent`).
6. **Rebase interativo** local antes do PR para limpar fix-ups e reordenar
   commits, mantendo cada commit autocontido.
7. **Tags SemVer** (`vMAJOR.MINOR.PATCH`) em `main` ao final de cada release.
8. **Release notes** geradas a partir dos commits via Conventional Commits.

### Branch protection rules (a aplicar na UI do GitHub)

- `main`:
  - Require pull request before merging.
  - Require status checks to pass (CI: ruff + mypy + pytest + build).
  - Require linear history.
  - Disallow force-push e deleção.
  - Restringir push direto (somente merge via PR).

### Gestão de crise

- **`git revert <sha>`** numa branch `hotfix/revert-<slug>` → PR → tag patch.
- **`git cherry-pick <sha>`** quando precisamos backportar um fix isolado
  para uma tag anterior (raríssimo; somente se existir release branch
  efêmera por exigência regulatória).
- **`release/vX.Y.Z` efêmera** é criada **somente sob demanda** quando uma
  versão precisa ser congelada para auditoria; recebe apenas fixes de
  release e é deletada após a tag.

## Consequências

### Positivas

- Histórico **linear, narrativo e auditável** (`git log --first-parent` lê
  como changelog).
- Pipeline de CI único e simples.
- Aderência total aos requisitos sênior/especialista do case.
- Custo cognitivo mínimo para reviewers externos.

### Negativas / Mitigações

- **Sem branch de homologação permanente** → mitigado por:
  - CI rodando pipeline completo em cada PR (qualidade gateada antes de
    chegar em `main`).
  - Ambiente de **staging** deployado a cada merge em `main` via Docker
    Compose (Etapa 11).
  - **Release branches efêmeras sob demanda** quando auditoria exigir.
- **Disciplina de PR-only** → mitigado por branch protection rule.

## Referências

- Driessen, V. — *A successful Git branching model* (2010, com nota de 2020).
- Chacon, S. — *GitHub Flow* (https://githubflow.github.io/).
- Humble, J. & Farley, D. — *Continuous Delivery* (2010).
- Skelton, M. & Pais, M. — *Team Topologies* (2019).
- Pyhrr, A. et al. — *Trunk Based Development* (trunkbaseddevelopment.com).
