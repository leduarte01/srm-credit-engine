# PR #27 — Hardening do LiveRateCurrencyConverter

> GitHub PRs: leduarte01/srm-credit-engine#25 + #26 + #27

## Summary

Três fixes encadeados que endurecem o conversor ao vivo introduzido no
PR #26 contra falhas observadas em produção:

1. **Exceções não tratadas** — qualquer erro HTTP (timeout, 5xx, JSON
   inválido) era propagado como 500 da API. Passa a ser capturado e
   convertido em `ExchangeRateNotFoundError`, ativando o fallback DB.
2. **Rate-limit do provedor** — AwesomeAPI retornava 429 sob carga.
   Migração para
   [fawazahmed0/exchange-api](https://github.com/fawazahmed0/exchange-api)
   (CDN jsDelivr + mirror Cloudflare Pages, sem auth, sem rate-limit).
3. **Cache TTL** — adiciona cache in-process de **60 s** por moeda
   base para reduzir round-trips e suavizar picos.

Inclui correções de tipo (`dict[str, Any]` em `_fetch_base_rates` para
`mypy strict`) e lint (`ruff`).

## Scope

- `backend/src/srm_credit_engine/infrastructure/live_rate_converter.py`
  — URLs primária/mirror, TTL cache, `try/except` abrangente.

## Quality gates

- Unit tests com `httpx.MockTransport` cobrindo timeout, 5xx, 429,
  JSON inválido → todos viram `ExchangeRateNotFoundError`.
- Validação de cache (segunda chamada não bate na rede).
