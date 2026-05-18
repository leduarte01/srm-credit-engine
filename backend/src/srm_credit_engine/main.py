"""FastAPI application entrypoint — wires routers, handlers and middleware."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from srm_credit_engine import __version__
from srm_credit_engine.api.v1 import router as v1_router
from srm_credit_engine.api.v1.errors import register_exception_handlers
from srm_credit_engine.config import get_settings
from srm_credit_engine.observability import (
    configure_logging,
    configure_tracing,
    metrics_response,
)
from srm_credit_engine.observability.middleware import ObservabilityMiddleware


def create_app() -> FastAPI:
    settings = get_settings()

    configure_logging(level=settings.log_level, json_format=settings.log_json)
    configure_tracing(
        service_name=settings.otel_service_name,
        service_version=__version__,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint or None,
        enabled=settings.app_env not in {"test", "ci"},
    )

    app = FastAPI(
        title="SRM Credit Engine",
        version=__version__,
        description=(
            "Plataforma de cessão de crédito multimoedas para Fundos de "
            "Investimento em Direitos Creditórios (FIDC). "
            "Expõe operações de cadastro, precificação e liquidação de recebíveis "
            "com trilha de auditoria por eventos."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.get("/health", tags=["meta"], summary="Liveness probe")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "version": __version__}

    if settings.prometheus_enabled:

        @app.get("/metrics", tags=["meta"], summary="Prometheus metrics scrape endpoint")
        async def metrics() -> object:
            return metrics_response()

    app.include_router(v1_router)

    return app


app = create_app()
