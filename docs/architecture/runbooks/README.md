# Runbooks — gestão de crise

Procedimentos operacionais para os incidentes mais prováveis. Cada
runbook responde: **Detecção**, **Diagnóstico**, **Mitigação**,
**Recuperação**, **Pós-mortem**.

| Incidente                                         | Runbook                                                 | Severidade |
| ------------------------------------------------- | ------------------------------------------------------- | ---------- |
| Provedor de câmbio (AwesomeAPI) indisponível      | [fx-outage.md](fx-outage.md)                            | P2         |
| PostgreSQL inacessível                            | [db-outage.md](db-outage.md)                            | P0         |
| Latência elevada / API lenta                      | [latency-spike.md](latency-spike.md)                    | P2         |
| Migração de banco falhou em produção              | [migration-failure.md](migration-failure.md)            | P1         |
| Suspeita de vazamento cross-tenant                | [tenant-leak.md](tenant-leak.md)                        | P0         |

## Severidades

| Nível | Definição                                                     | SLA de resposta |
| ----- | ------------------------------------------------------------- | --------------- |
| P0    | Indisponibilidade total ou risco de dado/auditoria.           | 15 min          |
| P1    | Funcionalidade crítica degradada para a maioria dos usuários. | 30 min          |
| P2    | Degradação parcial ou afeta minoria.                          | 2h              |
| P3    | Ruído operacional sem impacto direto.                         | 1 dia útil      |

## Princípios

1. **Estabilizar antes de explicar.** Mitigar é prioridade; root cause
   pode esperar.
2. **Comunicar cedo.** Toda P0/P1 abre um canal de incidente
   imediatamente.
3. **Não modifique dados em produção sem PR + revisão.** Hotfix segue
   [ADR-001](../../adr/ADR-001-branching-strategy.md).
4. **Tudo o que for tocado em produção fica documentado** no ticket de
   incidente.

## Pós-mortem padrão

Toda P0/P1 gera pós-mortem **blameless** com:

- Linha do tempo (UTC).
- Detecção: como soubemos?
- Impacto: tenants afetados, requests perdidos, dado corrompido?
- Causa raiz: cinco-porquês até origem técnica/processual.
- O que funcionou.
- O que não funcionou.
- Ações preventivas com **dono e prazo**.

Pós-mortems vivem em `docs/postmortems/YYYY-MM-DD-titulo.md`.
