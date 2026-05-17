# SRM Credit Engine

> Plataforma de cessão de crédito multimoedas (FIDC) — case técnico.
>
> Stack: **Python 3.12 + FastAPI** · **PostgreSQL 16** · **React + TS (Vite)** · **Docker Compose** · **OpenTelemetry + Prometheus + Grafana + Jaeger**

📄 Setup, arquitetura e decisões serão detalhados ao final do desenvolvimento.

Veja o plano de execução em [docs/PLAN.md](docs/PLAN.md) e o histórico de commits planejado em [docs/COMMITS.md](docs/COMMITS.md).

## Branching Strategy

Este projeto adota **GitHub Flow** com merges `--no-ff` e tags SemVer. A
justificativa completa (comparativo com Git Flow e Trunk Based, regras
operacionais e protocolo de hotfix) está documentada em
[docs/adr/ADR-001-branching-strategy.md](docs/adr/ADR-001-branching-strategy.md).

```
main (PRD, protegida, sempre deployável)
  ↑
  PR --no-ff (CI verde + revisão)
  │
feat/*  ·  fix/*  ·  chore/*  ·  docs/*  ·  hotfix/*
```

Convenções:

- **Conventional Commits 1.0.0** em toda mensagem.
- **PRs descritivos** em [docs/pull-requests/](docs/pull-requests/).
- **Branch protection** em `main`: PR obrigatório, CI verde, histórico linear.
- **Tags SemVer** (`vMAJOR.MINOR.PATCH`) em cada release.
- **ADRs** (Architecture Decision Records) em [docs/adr/](docs/adr/).
