"""Structured logging powered by :mod:`structlog`.

Renders JSON in production-like environments and a developer-friendly
console format otherwise. When OpenTelemetry is active, the current
``trace_id`` and ``span_id`` are merged into every record so logs and
traces correlate in any APM backend.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import structlog
from opentelemetry import trace
from structlog.types import EventDict, Processor


def _add_otel_context(_: object, __: str, event_dict: EventDict) -> EventDict:
    span = trace.get_current_span()
    if span is None:
        return event_dict
    context = span.get_span_context()
    if not context.is_valid:
        return event_dict
    event_dict.setdefault("trace_id", format(context.trace_id, "032x"))
    event_dict.setdefault("span_id", format(context.span_id, "016x"))
    return event_dict


def configure_logging(*, level: str = "INFO", json_format: bool = True) -> None:
    """Configure :mod:`structlog` and the stdlib root logger.

    Calling this function multiple times is safe — subsequent calls just
    overwrite the previous configuration.
    """
    numeric_level = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
        force=True,
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_otel_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer(colors=False)
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:  # noqa: ANN401 — structlog returns Any
    """Return a structlog logger bound to the given name."""
    return cast("Any", structlog.get_logger(name))
