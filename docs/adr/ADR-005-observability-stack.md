# ADR-005 — Stack de observabilidade: OpenTelemetry + Prometheus + structlog

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2026-04-12 | Engenharia |

## Contexto

O **SRM Credit Engine** opera dados financeiros e precisa atender três
demandas observacionais distintas:

1. **Tracing distribuído** — entender latência ponta-a-ponta de
   precificação (`HTTP → service → repo → provedor de câmbio`).
2. **Métricas agregadas** — SLOs (p95 latência, taxa de erro), saúde do
   circuit breaker, hit ratio de cache.
3. **Logs estruturados** — auditoria de ações de negócio
   (criação/atualização/liquidação de recebíveis) com correlação ao trace.

A escolha precisa ser **vendor-agnóstica** (não amarrar a DataDog/New
Relic), padronizada na indústria, e barata em produção.

## Opções avaliadas

### 1. Stack proprietária (DataDog APM completo)

- 👍 Plug-and-play, dashboards prontos.
- 👎 Vendor lock-in; custo alto em volume; agent intrusivo.

### 2. ELK + Jaeger + Prometheus, instrumentação manual

- 👍 Open source.
- 👎 Três SDKs distintos no código; sem semântica padronizada para
  correlação trace ↔ log ↔ métrica.

### 3. **OpenTelemetry (traces + métricas) + Prometheus exporter + structlog (logs)** ✅

- 👍 OTel é padrão CNCF; um único SDK para traces e métricas;
  intercambiável com qualquer backend (Tempo, Jaeger, DataDog, Honeycomb).
- 👍 Prometheus continua sendo o padrão para scraping de métricas;
  exporter OTel-→-Prom é nativo.
- 👍 structlog gera JSON com `trace_id`/`span_id` automaticamente
  injetados via `OpenTelemetryLoggingInstrumentor`.
- 👎 Curva de aprendizado de OTel é maior que SDKs proprietários.

## Decisão

### Camadas

| Sinal     | Instrumentação                                                   | Exporter / formato     |
| --------- | ---------------------------------------------------------------- | ---------------------- |
| Traces    | `opentelemetry-instrumentation-fastapi`, `sqlalchemy`, `httpx`, spans manuais em pricing | OTLP (gRPC) → coletor  |
| Métricas  | `opentelemetry-sdk-metrics` + counters/histograms manuais        | Prometheus `/metrics`  |
| Logs      | `structlog` JSON com processors `add_log_level`, `TimeStamper`, `OpenTelemetryProcessor` | stdout (coletor lê via fluentbit) |

### Convenções

- **Atributos OTel:** seguir [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
  (`http.route`, `db.statement`, `messaging.system`).
- **Atributos de domínio:** prefixo `srm.` (`srm.assignor_id`,
  `srm.receivable_id`) — nunca expor valores monetários como atributo
  (PII/auditoria).
- **Histogramas com buckets explícitos** para latência de pricing
  (`[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]`).
- **Logs sempre estruturados** — `logger.info("receivable.created", id=..., assignor_id=...)`.

### Health probes (não-OTel)

- `/health` — liveness barato (sem dependência externa).
- `/health/ready` — readiness com ping no PostgreSQL.
- `/metrics` — Prometheus scrape endpoint.

## Consequências

### Positivas

- Trocar de Jaeger para Tempo ou DataDog é mudança de variável de
  ambiente OTLP — código não muda.
- Toda métrica de Prometheus tem trace exemplar correspondente (exemplar
  feature do OTel/Prom).
- structlog produz JSON que serve de auditoria — `trace_id` permite
  amarrar log a span.

### Negativas (e mitigação)

- Coletor OTel é um componente extra (requer infra). Mitigado em dev
  com `--exporter=console`; em prod recomenda-se OpenTelemetry Collector
  como sidecar.
- structlog não é stdlib — mitigado pelo ecossistema maduro e zero
  dependência runtime crítica.

## Referências

- OpenTelemetry Semantic Conventions.
- _Distributed Tracing in Practice_ — Parker, Spoonhower, Mace (2020).
- Prometheus Best Practices — histogram bucket layout.
