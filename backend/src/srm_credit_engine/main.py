"""FastAPI application entrypoint (stub — populated by later etapas)."""

from __future__ import annotations

from fastapi import FastAPI

from srm_credit_engine import __version__
from srm_credit_engine.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SRM Credit Engine",
        version=__version__,
        description="Plataforma de cessão de crédito multimoedas (FIDC).",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    @app.get("/health", tags=["meta"], summary="Liveness probe")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "version": __version__}

    return app


app = create_app()
