# PR #19 — CD via webhook EasyPanel após CI

> GitHub PR: leduarte01/srm-credit-engine#16

## Summary

Fecha o ciclo CI/CD ligando GitHub Actions ao **EasyPanel**. Adiciona
um job `deploy` em `backend.yml` e `frontend.yml` que roda **apenas em
push para `main`**, condicionado ao sucesso do job `quality`. O passo
faz um `curl -X POST` em um deploy hook fornecido por secret
(`EASYPANEL_BACKEND_WEBHOOK` / `EASYPANEL_FRONTEND_WEBHOOK`),
disparando rebuild + rolling restart do serviço.

## Scope

- `.github/workflows/backend.yml` — novo job `deploy`.
- `.github/workflows/frontend.yml` — novo job `deploy`.
- Secrets configurados no repositório (não versionados).

## Quality gates

- CI passa em PR (deploy não roda em PR, só em `main`).
- Health-check em `/health/ready` valida o novo container.

## Rollback

Revert do commit em `main` redisparara CI + CD; alternativamente
redeploy de imagem anterior pelo painel do EasyPanel.
