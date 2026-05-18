# PR #4 — Lint fixes + uv lockfile + preservar case spec

> **Documento retroativo.** Este PR foi mergeado durante a Etapa 2 como
> uma correção transversal entre as etapas de bootstrap. O registro
> aqui completa a trilha de auditoria do
> diretório `docs/pull-requests/`.

## Summary
Correções de qualidade transversais e housekeeping aplicadas após o
bootstrap inicial. Não pertence a uma etapa específica do
[PLAN.md](../PLAN.md) — agrupa pequenas mudanças que apareceram
durante a execução das etapas 0–2 e precisaram entrar via PR
dedicado para manter o histórico linear.

## Scope
- `backend/uv.lock` — commit do lockfile do uv para builds
  reproduzíveis (`build(backend): commit uv lockfile for reproducible installs`).
- `backend/pyproject.toml` + ajustes em código — extração da constante
  ISO-4217 (3 dígitos) e remoção de regras `ruff` obsoletas
  (`fix(quality): extract ISO-4217 length constant and drop obsolete ruff rules`).
- `README_case_dev_srm.md` — preservação do enunciado original do case
  no repositório para fins de auditoria
  (`docs: preserve original technical case specification`).

## Architectural notes
- O lockfile é parte do contrato de reprodutibilidade: nenhum CI ou
  contêiner constrói sem `uv.lock` versionado.
- Manter o case spec dentro do repositório torna a comparação
  "escopo vs. entregue" reproduzível por qualquer revisor sem
  acesso ao canal de origem.

## Testing
- N/A — mudanças de configuração e documentação.

## Risks & Mitigations
- **Lockfile drift** — futuras atualizações de dependência precisam
  regerar o lockfile. Mitigação: `uv sync` regenera; CI quebra se o
  lockfile não bater com `pyproject.toml`.

## Out of Scope
- Mudanças funcionais no domínio ou na API.
