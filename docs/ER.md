# Modelo Entidade-Relacionamento — SRM Credit Engine

## Diagrama ER (Mermaid)

```mermaid
erDiagram
    CURRENCY ||--o{ EXCHANGE_RATE : "base"
    CURRENCY ||--o{ EXCHANGE_RATE : "quote"
    CURRENCY ||--o{ RECEIVABLE : "denominated_in"
    CURRENCY ||--o{ SETTLEMENT : "settled_in"

    PRODUCT_TYPE ||--o{ RECEIVABLE : "classified_as"
    ASSIGNOR     ||--o{ RECEIVABLE : "issued_by"
    RECEIVABLE   ||--|| SETTLEMENT : "originates"
    SETTLEMENT   ||--o{ SETTLEMENT_EVENT : "audited_by"

    CURRENCY {
        char(3)  code PK
        text     name
        smallint minor_unit
    }
    PRODUCT_TYPE {
        bigint   id PK
        text     code UK
        text     name
        numeric  monthly_spread "decimal(9,6)"
        boolean  active
    }
    ASSIGNOR {
        bigint   id PK
        text     tax_id UK "CNPJ"
        text     legal_name
        timestamp created_at
    }
    EXCHANGE_RATE {
        bigint     id PK
        char(3)    base_ccy FK
        char(3)    quote_ccy FK
        numeric    rate "decimal(20,10)"
        timestamp  valid_from
        timestamp  valid_to "nullable"
        text       source "MANUAL|MOCK_FEED"
    }
    RECEIVABLE {
        uuid     id PK
        bigint   assignor_id FK
        bigint   product_type_id FK
        char(3)  currency_code FK
        numeric  face_value "decimal(20,4)"
        date     issue_date
        date     due_date
        text     status "PENDING|PRICED|SETTLED|CANCELLED"
        int      version "optimistic lock"
        timestamp created_at
    }
    SETTLEMENT {
        uuid     id PK
        uuid     receivable_id FK UK
        char(3)  payment_currency FK
        numeric  base_rate_monthly "decimal(9,6)"
        numeric  spread_monthly "decimal(9,6)"
        numeric  present_value_original "decimal(20,4)"
        numeric  fx_rate_applied "decimal(20,10) nullable"
        numeric  net_amount_paid "decimal(20,4)"
        text     strategy_code
        timestamp settled_at
        int      version "optimistic lock"
    }
    SETTLEMENT_EVENT {
        bigint   id PK
        uuid     settlement_id FK
        text     event_type "CREATED|PRICED|CONFIRMED|FAILED"
        jsonb    payload
        timestamp occurred_at
    }
```

## Decisões de modelagem

| Decisão | Justificativa |
|---|---|
| `numeric` (PostgreSQL) com precisão explícita | Evita binário flutuante em valores monetários; aderente a normas contábeis. |
| `version` (int) em `receivable` e `settlement` | Habilita **Optimistic Locking** (evita race condition de liquidação dupla). |
| `exchange_rate` com `valid_from` / `valid_to` | Histórico temporal de taxas (auditoria + reproducibilidade de precificação). |
| `settlement_event` (jsonb) | Trilha de auditoria semi-estruturada; base para futura projeção EDA. |
| FK `currency` em quatro tabelas | Garante integridade referencial de moeda em toda a operação. |
| `uuid` para entidades transacionais | Evita colisões em sharding/replicação futuros (ver `HIGH_SCALE.md`). |
