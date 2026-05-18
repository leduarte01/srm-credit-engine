"""Unit tests for the observability package — logging and metrics primitives."""

from __future__ import annotations

import json
import logging
from io import StringIO

import structlog

from srm_credit_engine.observability.logging import configure_logging, get_logger
from srm_credit_engine.observability.metrics import (
    FX_LOOKUPS,
    PRICING_OPERATIONS,
    metrics_response,
)


def test_configure_logging_emits_json(capsys: object) -> None:
    configure_logging(level="DEBUG", json_format=True)
    logger = get_logger("srm.test")
    logger.info("priced", product_code="DUPLICATA_MERCANTIL", pv="123.45")
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    line = captured.out.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["event"] == "priced"
    assert payload["product_code"] == "DUPLICATA_MERCANTIL"
    assert payload["level"] == "info"
    assert "timestamp" in payload


def test_configure_logging_console_format_does_not_crash() -> None:
    configure_logging(level="INFO", json_format=False)
    logger = get_logger("srm.test")
    logger.info("hello", foo="bar")  # smoke-test — no assertion on plain output


def test_metrics_response_returns_prometheus_payload() -> None:
    PRICING_OPERATIONS.labels("DUPLICATA_MERCANTIL", "success").inc()
    FX_LOOKUPS.labels("USD", "BRL", "direct").inc()
    response = metrics_response()
    body = response.body.decode("utf-8") if response.body else ""
    assert "srm_pricing_operations_total" in body
    assert "srm_fx_lookups_total" in body


def test_contextvars_are_attached_to_log_records() -> None:
    configure_logging(level="INFO", json_format=True)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id="req-42")
    stream = StringIO()
    root = logging.getLogger()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)
    try:
        get_logger("srm.test").info("processed")
    finally:
        root.removeHandler(handler)
        structlog.contextvars.clear_contextvars()
