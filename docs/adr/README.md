# Architecture Decision Records (ADR)

Este diretório guarda decisões arquiteturais relevantes do projeto, no
formato leve proposto por Michael Nygard.

Cada arquivo descreve **contexto**, **opções avaliadas**, **decisão tomada**
e **consequências** (positivas e negativas). ADRs são imutáveis após
aceitos — mudanças geram um novo ADR que **supera** (`Supersedes`) o anterior.

## Índice

| ID  | Título                                                                          | Status |
| --- | ------------------------------------------------------------------------------- | ------ |
| 001 | [Branching Strategy: GitHub Flow](ADR-001-branching-strategy.md)                | Aceito |
| 002 | [Arquitetura Hexagonal (Ports & Adapters)](ADR-002-hexagonal-architecture.md)   | Aceito |
| 003 | [Decimal serializado como string](ADR-003-decimal-money.md)                     | Aceito |
| 004 | [Camadas de resiliência (retries + breaker + cache)](ADR-004-resilience-layering.md) | Aceito |
| 005 | [Observabilidade: OTel + Prometheus + structlog](ADR-005-observability-stack.md) | Aceito |
| 006 | [Multi-tenancy: single-DB com `tenant_id`](ADR-006-multi-tenancy.md)            | Aceito |
