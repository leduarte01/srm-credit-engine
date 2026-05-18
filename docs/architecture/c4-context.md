# C4 — Nível 1: Contexto do sistema

Visão de **mais alto nível**: o sistema como caixa única, suas pessoas
e seus integrantes externos.

```mermaid
C4Context
    title Contexto — SRM Credit Engine

    Person(analyst, "Analista de Crédito", "Cadastra cedentes, lança recebíveis, executa pricing e liquida operações.")
    Person(ops, "Operações / Tesouraria", "Acompanha carteira agregada e relatórios diários.")
    Person(auditor, "Auditor Interno", "Consulta histórico imutável de cotações e liquidações.")

    System(srm, "SRM Credit Engine", "Plataforma de gestão de FIDC: cedentes, recebíveis, pricing, liquidações e analytics.")

    System_Ext(fx, "Provedor de Câmbio (AwesomeAPI)", "Cotações spot por par de moedas.")
    System_Ext(otel, "Backend de Observabilidade", "Tempo / Jaeger / Prometheus / Grafana.")

    Rel(analyst, srm, "Usa via navegador (SPA React)")
    Rel(ops, srm, "Consulta relatórios e dashboards")
    Rel(auditor, srm, "Lê audit trail (somente leitura)")

    Rel(srm, fx, "GET /json/last/{pair}", "HTTPS")
    Rel(srm, otel, "Exporta traces (OTLP) e métricas (Prometheus)", "OTLP/gRPC, HTTP")

    UpdateRelStyle(analyst, srm, $offsetY="-10")
    UpdateRelStyle(srm, fx, $offsetX="40")
```

## Pessoas (atores)

| Ator                     | Necessidade primária                                              |
| ------------------------ | ----------------------------------------------------------------- |
| **Analista de Crédito**  | Cadastrar cedente, lançar recebível, precificar e liquidar.       |
| **Operações/Tesouraria** | Visão consolidada da carteira; conciliação diária.                |
| **Auditor Interno**      | Audit trail imutável de cotações usadas e operações realizadas.   |

## Sistemas externos

| Sistema             | Propósito                                            | Tipo de integração       |
| ------------------- | ---------------------------------------------------- | ------------------------ |
| **AwesomeAPI**      | Cotação spot para precificação em moeda estrangeira. | HTTPS REST, pull, cache. |
| **Coletor OTel**    | Tracing distribuído e métricas.                      | OTLP/gRPC saindo.        |
| **Prometheus**      | Scrape de métricas em `/metrics`.                    | HTTP entrando.           |

## Princípios de fronteira

- **Nenhum sistema externo no caminho crítico de leitura** — pricing
  serve a partir do cache de cotações no PostgreSQL quando possível.
- **Auditoria nunca depende do provedor de câmbio** — toda cotação usada
  vira linha em `exchange_rate`.
- **Observabilidade nunca bloqueia o request** — OTel é exportador
  assíncrono.
