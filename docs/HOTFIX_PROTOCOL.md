# Protocolo de Hotfix

> Protocolo operacional para corrigir defeitos críticos em produção
> sem manter branches de longa duração. Decorre da estratégia de
> branching declarada em
> [ADR-001](adr/ADR-001-branching-strategy.md).

## Quando usar

Use o protocolo de hotfix **somente** quando:

- A versão atualmente em produção (`main` na última tag SemVer)
  contém um defeito de severidade **P0** ou **P1** (ver
  [runbooks](architecture/runbooks/README.md) para severidades).
- O fix é **pequeno e isolado** (≤ 100 linhas; ≤ 3 arquivos
  tipicamente).
- Não dá para esperar o próximo merge regular.

Caso contrário, siga o fluxo normal (`feat/*`, `fix/*`, `docs/*`)
com revisão padrão.

## Princípios

1. **`main` sempre deployável.** Toda correção entra via PR `--no-ff`
   com CI verde.
2. **Tag SemVer obrigatória.** Hotfix incrementa `PATCH`
   (`v1.0.0 → v1.0.1`).
3. **Sem branch de longa duração.** Nada de `release/*` permanente
   nem `develop`.
4. **`git revert` precede `git cherry-pick`.** Se um commit ruim
   chegou a `main`, **reverte primeiro** — devolve o sistema a um
   estado saudável; depois aplica o fix correto via cherry-pick ou
   PR novo.
5. **Tudo documentado.** Cada hotfix gera entrada no
   [CHANGELOG](../CHANGELOG.md) e um PR com descrição em
   [docs/pull-requests/](pull-requests/).

## Variantes

### A) Hotfix simples — bug existia antes da release

Fluxo padrão de PR sobre `main`.

```bash
# 1. Garantir que main está atualizado e limpo
git checkout main
git pull --ff-only

# 2. Criar branch de hotfix
git checkout -b hotfix/v1.0.1-fx-cache-ttl

# 3. Fazer o fix, commit em Conventional Commits
git add backend/src/srm_credit_engine/infrastructure/database_currency_converter.py
git commit -m "fix(fx): clamp cache TTL to non-negative values"

# 4. Push e PR (--no-ff no merge)
git push -u origin hotfix/v1.0.1-fx-cache-ttl
# abrir PR no GitHub; aguardar CI; merge com botão "Create a merge commit"

# 5. Tag anotada na main após merge
git checkout main
git pull --ff-only
git tag -a v1.0.1 -m "fix(fx): clamp cache TTL to non-negative values"
git push origin v1.0.1
```

### B) Hotfix por reversão — commit ruim já em `main`

Use quando um commit específico já mergeado provocou o incidente. O
`git revert` cria um **novo commit que desfaz** o commit ruim,
preservando a história linear.

```bash
# 1. Identificar o commit responsável
git log --oneline --first-parent main

# 2. Reverter (gera commit "Revert ...")
git checkout main
git pull --ff-only
git checkout -b hotfix/v1.0.1-revert-broken-pricing
git revert <sha-do-commit-ruim>           # conflito? resolver e git commit
git push -u origin hotfix/v1.0.1-revert-broken-pricing

# 3. PR --no-ff → merge → tag
git checkout main
git pull --ff-only
git tag -a v1.0.1 -m "revert: roll back broken pricing change"
git push origin v1.0.1
```

> ⚠️ **Nunca** rode `git revert` direto em `main` localmente e
> faça push. Sempre via branch + PR.

### C) Hotfix por cherry-pick — fix existe em outra branch

Use quando o fix correto já foi commitado em uma branch de feature
em andamento mas você precisa entregar antes do merge geral. Cherry-
pick traz **somente** aquele commit para `main`.

```bash
# 1. Pegar o SHA do commit que carrega o fix
git log --oneline feat/big-refactor    # achar o SHA exato

# 2. Branch de hotfix a partir de main
git checkout main
git pull --ff-only
git checkout -b hotfix/v1.0.1-cherrypick-fx-timeout

# 3. Trazer o commit
git cherry-pick <sha>                  # conflito? resolver e git cherry-pick --continue

# 4. PR --no-ff → merge → tag
git tag -a v1.0.1 -m "fix(fx): tighten HTTP timeout to 3s"
git push origin v1.0.1
```

> 💡 Se o commit não existe ainda — escreva o fix em `hotfix/*`
> direto (variante A) e, depois, cherry-pick o mesmo commit para a
> branch de feature em andamento.

## Worked example — receita pedagógica (não executada)

> ⚠️ **Esta seção é demonstração**, não um registro histórico. Os
> comandos abaixo **não foram aplicados** ao repositório — servem
> como roteiro reproduzível que um operador segue quando um
> incidente real acontecer. Para ver o protocolo aplicado de
> verdade, consulte o histórico git em torno das tags `v1.0.1` ou
> superiores, **se** elas existirem.

Cenário fictício realista usado como demonstração do protocolo:

> "Em produção da `v1.0.0`, o gate de cobertura do CI passou a
> rejeitar PRs porque o limiar estava configurado como 80 mas um
> teste foi removido sem cobertura compensatória. A correção exige
> aumentar a cobertura — não relaxar o gate."

### Passo a passo (template)

```bash
# 1. Estado inicial — main na tag v1.0.0
git checkout main
git pull --ff-only
git describe --tags --abbrev=0     # → v1.0.0

# 2. Branch de hotfix
git checkout -b hotfix/v1.0.1-coverage-restore

# 3. Adicionar testes que recuperam a cobertura
git add backend/tests/unit/test_pricing_invariants.py
git commit -m "fix(tests): restore coverage gate by adding missing pricing invariants"

# 4. Push + PR --no-ff
git push -u origin hotfix/v1.0.1-coverage-restore
#   → PR aberto, CI verde, merge --no-ff em main

# 5. Tag anotada
git checkout main && git pull --ff-only
git tag -a v1.0.1 -m "fix: restore coverage gate"
git push origin v1.0.1

# 6. Atualizar CHANGELOG (entrada nova [1.0.1])
#   commit segue como parte do próximo PR de manutenção
```

> Quando um hotfix **real** for executado seguindo este protocolo,
> a tag SemVer subsequente (`v1.0.1`, `v1.0.2`, …) e o commit de
> revert/cherry-pick correspondente ficarão preservados na história
> git, e esta seção pode ser referenciada como o procedimento
> seguido.

## Pós-hotfix — checklist obrigatório

- [ ] Tag SemVer anotada criada e enviada (`git push origin vX.Y.Z`).
- [ ] CHANGELOG atualizado com seção `[X.Y.Z] — YYYY-MM-DD`.
- [ ] Incidente que disparou o hotfix tem **pós-mortem blameless**
      em `docs/postmortems/YYYY-MM-DD-titulo.md` (P0/P1 apenas).
- [ ] Causa raiz resultou em **teste de regressão** que reprovaria
      o defeito antes do merge.
- [ ] Métrica/alerta foi adicionado ou ajustado se a detecção
      tardou.
- [ ] Se o hotfix foi `revert`, abrir issue para retomar a feature
      com correção.

## Anti-padrões proibidos

- ❌ Tag direto em `main` sem PR e merge `--no-ff`.
- ❌ Force-push em `main` para "limpar" o histórico.
- ❌ Reescrever commit já mergeado (`git rebase -i`, `git commit --amend`).
- ❌ Pular CI com `--no-verify` no commit ou bypass de proteção de branch.
- ❌ Hotfix sem teste de regressão.
- ❌ Esquecer de aplicar o mesmo fix em branches longas em andamento
      (use cherry-pick).

## Comunicação durante o incidente

| Momento                | Canal                         | Conteúdo mínimo                  |
| ---------------------- | ----------------------------- | -------------------------------- |
| Início do hotfix       | Canal de incidente            | Severidade, owner, ETA estimado  |
| PR aberto              | Canal de incidente            | Link do PR + status do CI        |
| Merge concluído        | Canal de incidente            | Tag SemVer atribuída             |
| Deploy concluído       | Canal de incidente + público  | Confirmação que produção voltou  |
| Pós-mortem publicado   | Canal de engenharia           | Link do `docs/postmortems/`      |
