# PR #1 — Bootstrap do repositório

**Branch:** `chore/bootstrap` → `main`
**Tipo:** chore

## O que foi feito
- Inicializa repositório git com estrutura mínima
- Adiciona `README.md` placeholder com stack escolhida
- Adiciona `LICENSE` (MIT)
- Adiciona `.gitignore` para Python + Node
- Adiciona `.editorconfig` (LF, UTF-8, 4 espaços Python / 2 espaços JSON/MD/JS)
- Adiciona `.gitattributes` para normalizar EOL entre Windows/Linux/Mac
- Adiciona `docs/PLAN.md` com plano de execução detalhado em 15 etapas
- Adiciona `docs/COMMITS.md` (histórico vivo)

## Por que
Estabelece a base de governança do repositório (commits atômicos, padronização de formatação, line endings consistentes via `.editorconfig` e `.gitattributes`) antes de qualquer código de aplicação. Garante que toda contribuição posterior nasça sobre um terreno reprodutível e pronto para hooks de pre-commit e pipeline de CI.

## Checklist
- [x] Conventional Commits aplicados
- [x] Branch específica (não trabalhar direto na `main`)
- [x] PR descrito
