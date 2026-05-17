"""Async SQLAlchemy engine, session factory and FastAPI dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from srm_credit_engine.config import Settings, get_settings


@lru_cache(maxsize=1)
def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """Return a process-wide async engine. Cached for the lifetime of the app."""
    cfg = settings or get_settings()
    return create_async_engine(
        cfg.database_url,
        echo=False,
        pool_size=cfg.database_pool_size,
        max_overflow=cfg.database_max_overflow,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Context manager that opens a transactional session."""
    factory = get_sessionmaker()
    async with factory() as session, session.begin():
        yield session


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a transactional session per request."""
    factory = get_sessionmaker()
    async with factory() as session, session.begin():
        yield session
