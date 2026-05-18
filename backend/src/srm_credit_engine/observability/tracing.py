"""OpenTelemetry tracing setup.

The exporter is optional: when no OTLP endpoint is reachable the SDK still
attaches valid spans to outgoing logs and metrics, but no data is shipped.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

_logger = logging.getLogger(__name__)


class _State:
    configured: bool = False


def configure_tracing(
    *,
    service_name: str,
    service_version: str,
    otlp_endpoint: str | None = None,
    enabled: bool = True,
) -> None:
    """Install a :class:`TracerProvider` for the process.

    When ``otlp_endpoint`` is provided the SDK ships spans to an OTLP/gRPC
    collector. When ``enabled=False`` the function is a no-op (useful for
    tests and CI).
    """
    if _State.configured or not enabled:
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        }
    )
    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        try:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception as exc:  # pragma: no cover — defensive
            _logger.warning("otel_exporter_init_failed", exc_info=exc)

    trace.set_tracer_provider(provider)
    _State.configured = True


def instrument_app(app: FastAPI, engine: AsyncEngine | None = None) -> None:
    """Attach OTel instrumentation to a FastAPI app and a SQLAlchemy engine."""
    FastAPIInstrumentor.instrument_app(app)
    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
