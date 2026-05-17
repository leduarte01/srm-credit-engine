# Histórico de Commits

Este documento traz a sequência de commits planejada. Os commits reais são feitos durante o desenvolvimento — este arquivo é atualizado ao final de cada etapa para fins de rastreabilidade.

## Convenção

[Conventional Commits 1.0.0](https://www.conventionalcommits.org/).

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

## Histórico

### Etapa 0 — Bootstrap (`chore/bootstrap` → `main`)
- `chore: initialize repository structure and plan`
- `chore: add gitignore and editorconfig for Python + Node stack`
- `docs: add commits log placeholder`
- `chore: add gitattributes and PR-001 description`

### Etapa 1 — Modelagem de dados (`feat/data-model` → `main`)
- `docs(data): add ER diagram for credit engine`
- `feat(db): create initial schema with currencies, products, receivables, settlements`
- `docs: add PR-002 description`
- `Merge PR #2: data model (ER + DDL)`

### Etapa 2 — Backend Bootstrap (`feat/backend-bootstrap` → `main`)
- `chore(backend): scaffold python project with uv, ruff, mypy strict, pytest`
- `feat(api): add FastAPI app skeleton with settings and healthcheck`
- `feat(domain): add Money value object and DomainError hierarchy`
- `test(domain): cover Money invariants and decimal safety`
- `docs: add PR-003 description`
- `Merge PR #3: backend bootstrap (Python + FastAPI scaffolding)`
