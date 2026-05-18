# Runbook — PostgreSQL inacessível

**Severidade:** P0 (sistema fora do ar).

## Detecção

| Sinal                                            | Origem                       |
| ------------------------------------------------ | ---------------------------- |
| `/health/ready` retornando 503                   | Probe Kubernetes / ALB       |
| Aumento abrupto de 5xx em `/api/v1/*`            | nginx / API gateway          |
| Logs `event=db.connect.failed`                   | structlog                    |
| Alert `up{job="postgresql"} == 0`                | Prometheus (postgres_exporter) |

## Diagnóstico (≤ 5 min)

1. Conferir status do managed PostgreSQL (RDS / Cloud SQL console).
2. Tentar `psql` direto do bastion: `psql -h <host> -U <user> -d <db>`.
3. Inspecionar `pg_stat_activity` em réplica de leitura (se DB primário
   morto):
   ```sql
   SELECT pid, state, wait_event, query FROM pg_stat_activity
   WHERE state != 'idle' ORDER BY query_start;
   ```
4. Métricas: `pg_stat_database.numbackends`, CPU, disk IOPS, conexões
   no PgBouncer (se aplicável).

## Cenários e mitigação

### A) Saturação de conexões

**Sinal:** `numbackends ≈ max_connections`; novos clientes recebem
`FATAL: too many connections`.

**Mitigação imediata:**
1. Identificar query consumidora:
   ```sql
   SELECT pid, age(clock_timestamp(), query_start), query
   FROM pg_stat_activity WHERE state = 'active'
   ORDER BY query_start LIMIT 20;
   ```
2. Cancelar queries longas (> 5 min) com `SELECT pg_cancel_backend(pid);`.
3. Reduzir pool da aplicação (`DATABASE_POOL_SIZE=5`) e re-deployar.

**Prevenção:** introduzir PgBouncer (ver
[high-scale §1](../high-scale.md)).

### B) Disco cheio

**Sinal:** `pg_stat_database` para de avançar; `disk_free_bytes < 5%`.

**Mitigação:**
1. **Não rodar VACUUM FULL** durante o incidente — bloqueia.
2. Expandir storage (managed: aumentar GB; self-hosted: anexar volume).
3. Truncar tabelas de log/audit não essenciais com retenção excedida
   (apenas com aprovação).

### C) Réplica primária caiu

**Sinal:** failover automatic ou manual disparado.

**Mitigação:**
1. Confirmar failover concluído (managed services fazem automaticamente).
2. App reabre conexões automaticamente (asyncpg pool com `pool_recycle`).
3. Se DNS não atualizou: reiniciar pods do backend.

### D) Migração travada

Ver [migration-failure.md](migration-failure.md).

## Recuperação

1. Esperar `/health/ready` voltar a 200.
2. Backfill de requests falhados: o frontend retenta automaticamente
   leituras; mutações exigem reenvio manual do usuário.
3. Conferir integridade:
   ```sql
   SELECT pg_database_size(current_database());
   SELECT count(*) FROM receivable WHERE created_at > now() - interval '1 hour';
   ```

## Verificação pós-incidente

- [ ] Backup mais recente é íntegro.
- [ ] Nenhuma escrita foi perdida (cruzar com logs estruturados).
- [ ] WAL archiving funcionou durante todo o período (se aplicável).
- [ ] Pós-mortem aberto.

## Prevenção

- Monitorar `numbackends / max_connections > 0.7` com alerta.
- Monitorar `disk_free_pct < 20%`.
- Plano de capacity review trimestral.
