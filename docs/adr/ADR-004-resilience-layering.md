# ADR-004 — Camadas de resiliência para integração de câmbio (retries + circuit breaker + cache)

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2026-04-12 | Engenharia |

## Contexto

O **SRM Credit Engine** consome um provedor externo de câmbio
(AwesomeAPI) para precificar recebíveis em moedas distintas da moeda do
fundo. Esse provedor é:

- **Indisponível ocasionalmente** (HTTP 5xx, timeout).
- **Rate-limitado** (HTTP 429 esporádico).
- **Não-transacional** — pode falhar no meio de uma precificação de
  lote.

Falhar a precificação por causa de instabilidade externa é inaceitável.
O sistema precisa **degradação graciosa** sem comprometer auditoria.

## Opções avaliadas

### 1. Chamada direta sem proteção

- 👎 Qualquer 5xx aborta a operação de negócio. Inaceitável.

### 2. Retry exponencial somente

- 👍 Lida com falhas transitórias.
- 👎 Sob falha sustentada, multiplica latência para o usuário e gera
  carga adicional no provedor (anti-padrão "retry storm").

### 3. **Retry + Circuit Breaker + Cache de cotações no banco** ✅

Três camadas combinadas como decorators em torno de `CurrencyConverter`:

- **Cache (camada interna, mais próxima do domínio):** consulta
  `exchange_rate` no PostgreSQL antes de chamar o provedor; TTL
  configurável; resposta de provedor é gravada como nova linha
  (histórico imutável).
- **Circuit breaker (camada intermediária):** após N falhas consecutivas
  em janela curta, abre o circuito por T segundos — chamadas falham
  rápido sem tocar o provedor.
- **Retry (camada externa, mais próxima da rede):** tenacity com
  exponencial + jitter, somente em códigos transitórios (5xx, 429,
  timeouts).

## Decisão

Composição definida no Composition Root (`api/v1/deps.py`):

```python
provider = HttpCurrencyProvider(...)          # cliente HTTP cru
retried  = with_retries(provider)             # tenacity decorator
breaker  = with_circuit_breaker(retried)      # purgatory decorator
cache    = DatabaseCurrencyConverter(breaker, session_factory)  # cache no DB
domain_port: CurrencyConverter = cache
```

### Parâmetros

| Camada          | Biblioteca | Configuração                                                       |
| --------------- | ---------- | ------------------------------------------------------------------ |
| Retry           | tenacity   | 3 tentativas, exp backoff base 0.5s, jitter ±20%, somente 5xx/429/timeout |
| Circuit Breaker | purgatory  | threshold=5, recovery=30s, half-open com 1 probe                   |
| Cache           | PostgreSQL | TTL configurável (default 3600s) por par de moedas                 |

### Garantias

- **Idempotência:** chamada `convert(amount, from, to)` é
  referencialmente transparente dentro do TTL.
- **Observabilidade:** cada camada exporta métricas Prometheus
  (`exchange_rate_cache_hits_total`,
  `exchange_rate_retries_total`,
  `exchange_rate_breaker_state`).
- **Trace correlation:** spans OTel `cache → breaker → retry → http`.

## Consequências

### Positivas

- Indisponibilidade do provedor não derruba pricing — cache resolve a
  maioria dos casos.
- Retry storm prevenido por circuit breaker.
- Histórico imutável de cotações em `exchange_rate` é insumo direto para
  auditoria.

### Negativas (e mitigação)

- Cache pode servir cotação ligeiramente desatualizada — mitigado por
  TTL curto em cenário transacional e métrica de _staleness_.
- Decorator stack aumenta latência base — mitigado por circuit breaker
  curto-circuitando rápido em falha sustentada.

## Referências

- Michael Nygard, _Release It!_ — Stability Patterns.
- tenacity (Python) — Joshua Harlow.
- purgatory — circuit breaker assíncrono.
