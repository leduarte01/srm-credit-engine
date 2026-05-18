# Runbook — Pico de latência / API lenta

**Severidade:** P2 (eleva-se a P1 se p95 > 5s sustentado).

## Detecção

- Alerta Prometheus:
  ```promql
  histogram_quantile(0.95,
    sum by (le, route) (rate(srm_http_request_duration_seconds_bucket[5m]))
  ) > 1.0
  ```
- Aumento de logs com `duration_ms > 1000`.

## Diagnóstico — árvore de decisão

```
1. p95 alto em qual rota?
   ├─ /api/v1/pricing*  → suspeita FX (provider lento) ou DB lento
   ├─ /api/v1/reports*  → query analytics pesada
   ├─ /api/v1/receivables (GET list) → falta de índice / paginação ruim
   └─ Generalizado     → gargalo de DB ou pool de conexões saturado

2. DB ativo está saturado?
   ├─ Sim → ver db-outage cenário A (saturação conexões)
   └─ Não → seguir 3

3. Provedor de câmbio responde lento?
   ├─ Sim → ver fx-outage.md
   └─ Não → seguir 4

4. Tracing OTel: identificar span dominante
   ├─ db.query duro → faltou índice ou query nova ruim
   ├─ http.client (fx) → ajustar timeout/cache
   └─ pricing.calculate → algoritmo novo regrediu
```

## Diagnóstico (≤ 10 min)

1. **Top endpoints por latência:**
   ```promql
   topk(5,
     histogram_quantile(0.95,
       sum by (le, route) (rate(srm_http_request_duration_seconds_bucket[5m]))
     )
   )
   ```
2. **Top queries em PostgreSQL:**
   ```sql
   SELECT query, calls, mean_exec_time, total_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC LIMIT 20;
   ```
3. **Traces representativos** no Tempo/Jaeger filtrando
   `duration > 1s`.
4. **Saturação do pool:**
   ```promql
   srm_db_pool_checked_out / srm_db_pool_size
   ```

## Mitigação

| Causa identificada                | Ação imediata                                                 |
| --------------------------------- | ------------------------------------------------------------- |
| Query nova sem índice             | `CREATE INDEX CONCURRENTLY ...` (revisar antes!)              |
| Pool de conexões saturado         | Aumentar `DATABASE_POOL_SIZE`; ou escalar réplicas backend    |
| Provider de câmbio lento          | Estender TTL cache (`EXCHANGE_RATE_CACHE_TTL_SECONDS`)        |
| Regressão de pricing              | Rollback do deploy (`git revert` + redeploy)                  |
| Tráfego de relatório dominante    | Mover para read replica (se já provisionada)                  |
| Hot tenant                        | Rate-limit temporário por `X-Tenant-Id`                       |

## Recuperação

1. p95 retorna ao baseline em < 10 min após mitigação.
2. Cancelar mudanças temporárias (TTL, pool) após estabilização.
3. Abrir PR com fix permanente (índice, otimização) seguindo
   ADR-001.

## Prevenção

- Toda nova query é revisada com `EXPLAIN ANALYZE` antes de merge.
- Endpoints novos têm teste de carga mínimo (k6 ou similar) no PR.
- Histogramas Prometheus com buckets revisados por endpoint.
