-- =====================================================================
-- SRM Credit Engine — DDL (PostgreSQL 16)
-- Migration V1__init.sql
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------- Moedas ----------
CREATE TABLE currency (
    code        CHAR(3)     PRIMARY KEY,
    name        TEXT        NOT NULL,
    minor_unit  SMALLINT    NOT NULL DEFAULT 2
);

INSERT INTO currency (code, name, minor_unit) VALUES
    ('BRL', 'Real Brasileiro', 2),
    ('USD', 'US Dollar',       2);

-- ---------- Taxas de câmbio (histórico temporal) ----------
CREATE TABLE exchange_rate (
    id          BIGSERIAL   PRIMARY KEY,
    base_ccy    CHAR(3)     NOT NULL REFERENCES currency(code),
    quote_ccy   CHAR(3)     NOT NULL REFERENCES currency(code),
    rate        NUMERIC(20,10) NOT NULL CHECK (rate > 0),
    valid_from  TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to    TIMESTAMPTZ NULL,
    source      TEXT        NOT NULL DEFAULT 'MANUAL',
    CHECK (base_ccy <> quote_ccy),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);
CREATE INDEX idx_fx_pair_validity
    ON exchange_rate (base_ccy, quote_ccy, valid_from DESC);

-- ---------- Tipos de Produto (recebíveis) ----------
CREATE TABLE product_type (
    id              BIGSERIAL   PRIMARY KEY,
    code            TEXT        NOT NULL UNIQUE,
    name            TEXT        NOT NULL,
    monthly_spread  NUMERIC(9,6) NOT NULL CHECK (monthly_spread >= 0),
    active          BOOLEAN     NOT NULL DEFAULT TRUE
);

INSERT INTO product_type (code, name, monthly_spread) VALUES
    ('DUPLICATA',    'Duplicata Mercantil', 0.015),
    ('CHEQUE_PRE',   'Cheque Pré-datado',   0.025),
    ('CONTRATO_USD', 'Contrato em USD',     0.012);

-- ---------- Cedentes ----------
CREATE TABLE assignor (
    id          BIGSERIAL   PRIMARY KEY,
    tax_id      TEXT        NOT NULL UNIQUE,
    legal_name  TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------- Recebíveis ----------
CREATE TABLE receivable (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    assignor_id     BIGINT      NOT NULL REFERENCES assignor(id),
    product_type_id BIGINT      NOT NULL REFERENCES product_type(id),
    currency_code   CHAR(3)     NOT NULL REFERENCES currency(code),
    face_value      NUMERIC(20,4) NOT NULL CHECK (face_value > 0),
    issue_date      DATE        NOT NULL,
    due_date        DATE        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','PRICED','SETTLED','CANCELLED')),
    version         INTEGER     NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (due_date >= issue_date)
);
CREATE INDEX idx_receivable_assignor ON receivable (assignor_id);
CREATE INDEX idx_receivable_status   ON receivable (status);

-- ---------- Liquidações ----------
CREATE TABLE settlement (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receivable_id           UUID        NOT NULL UNIQUE REFERENCES receivable(id),
    payment_currency        CHAR(3)     NOT NULL REFERENCES currency(code),
    base_rate_monthly       NUMERIC(9,6)   NOT NULL,
    spread_monthly          NUMERIC(9,6)   NOT NULL,
    present_value_original  NUMERIC(20,4)  NOT NULL,
    fx_rate_applied         NUMERIC(20,10) NULL,
    net_amount_paid         NUMERIC(20,4)  NOT NULL,
    strategy_code           TEXT           NOT NULL,
    settled_at              TIMESTAMPTZ    NOT NULL DEFAULT now(),
    version                 INTEGER        NOT NULL DEFAULT 0
);
CREATE INDEX idx_settlement_settled_at      ON settlement (settled_at);
CREATE INDEX idx_settlement_payment_ccy     ON settlement (payment_currency);

-- ---------- Trilha de auditoria de liquidação ----------
CREATE TABLE settlement_event (
    id              BIGSERIAL   PRIMARY KEY,
    settlement_id   UUID        NOT NULL REFERENCES settlement(id) ON DELETE CASCADE,
    event_type      TEXT        NOT NULL,
    payload         JSONB       NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_settlement_event_settlement ON settlement_event (settlement_id);

-- ---------- Seed: cedentes e taxa USD/BRL ----------
INSERT INTO assignor (tax_id, legal_name) VALUES
    ('12345678000190', 'Cedente Demo LTDA'),
    ('98765432000110', 'Global Trade S/A');

INSERT INTO exchange_rate (base_ccy, quote_ccy, rate, source) VALUES
    ('USD', 'BRL', 5.0500000000, 'MANUAL'),
    ('BRL', 'USD', 0.1980000000, 'MANUAL');
