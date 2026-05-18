# Runbook — Provedor de câmbio indisponível

**Severidade:** P2 (a arquitetura tolera; ver [ADR-004](../../adr/ADR-004-resilience-layering.md))

## Detecção

| Sinal                                              | Origem                            |
| -------------------------------------------------- | --------------------------------- |
| Alerta `srm_exchange_rate_breaker_state == 1`      | Prometheus / Grafana              |
| Aumento de `srm_exchange_rate_retries_total`       | Prometheus                        |
| Latência p95 de pricing > 2s                       | Prometheus                        |
| Logs `event=fx.fetch.failed` recorrentes           | structlog                         |

## Diagnóstico (≤ 5 min)

1. Confirmar estado do breaker:
   ```promql
   max_over_time(srm_exchange_rate_breaker_state[5m])
   ```
2. Status público do provedor (AwesomeAPI status page, se houver).
3. `curl -v https://economia.awesomeapi.com.br/json/last/USD-BRL`
   a partir de um pod do backend para isolar problema de rede.
4. Inspecionar trace recente em Tempo/Jaeger:
   `service.name=srm-credit-engine` + `error=true`.

## Mitigação

A arquitetura **já degrada graciosamente**:

- Cache em DB serve cotações dentro do TTL.
- Circuit breaker corta chamadas a partir de N falhas.
- Retries com jitter já tentaram antes do breaker abrir.

### Ações operacionais

1. **Estender TTL temporariamente** se cotações ficarem stale:
   ```bash
   # variável de ambiente (sem deploy)
   kubectl set env deployment/backend EXCHANGE_RATE_CACHE_TTL_SECONDS=14400
   ```
2. **Avisar usuários** quando staleness > 1h (banner no SPA via flag
   `system_status`).
3. **Bloquear novas precificações de moedas sem cache válido** se
   compliance exigir cotação fresca (config `STRICT_FX_FRESHNESS=true`).

### Não fazer

- ❌ Forçar bypass do breaker (`RESILIENCE_BREAKER_ENABLED=false`).
  Isso reabre _retry storm_ contra o provedor.
- ❌ Editar tabela `exchange_rate` manualmente.

## Recuperação

1. Aguardar healthcheck do provedor voltar (provedor externo).
2. Breaker entra em **half-open** após `recovery_seconds`; uma chamada
   probe é enviada.
3. Se sucesso → breaker fecha automaticamente.
4. Métrica `srm_exchange_rate_breaker_state` retorna a 0.
5. Reverter `EXCHANGE_RATE_CACHE_TTL_SECONDS` ao default.

## Verificação pós-incidente

- [ ] Hit ratio do cache durante o incidente foi documentado.
- [ ] Nenhuma cotação stale foi usada em settlement crítico (cruzar
      `exchange_rate.fetched_at` com `settlement.created_at`).
- [ ] Pós-mortem aberto se duração > 30 min.

## Prevenção (médio prazo)

- Avaliar **provedor secundário de câmbio** (fallback) com novo
  adaptador `FallbackCurrencyConverter` no Composition Root.
- Considerar cache _pre-warm_ noturno para pares de moedas mais usados.
