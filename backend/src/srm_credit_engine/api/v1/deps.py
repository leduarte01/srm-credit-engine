"""FastAPI dependency wiring — keeps routers free of construction logic."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from srm_credit_engine.config import Settings, get_settings
from srm_credit_engine.domain.ports.analytics import AnalyticsRepository
from srm_credit_engine.domain.ports.currency_converter import CurrencyConverter
from srm_credit_engine.domain.ports.repositories import (
    AssignorRepository,
    ExchangeRateRepository,
    ProductTypeRepository,
    ReceivableRepository,
    SettlementRepository,
)
from srm_credit_engine.domain.pricing.resolver import PricingStrategyResolver
from srm_credit_engine.domain.services.pricing_service import PricingService
from srm_credit_engine.infrastructure.analytics_repository import SqlAnalyticsRepository
from srm_credit_engine.infrastructure.database import get_session
from srm_credit_engine.infrastructure.database_currency_converter import (
    DatabaseCurrencyConverter,
)
from srm_credit_engine.infrastructure.repositories import (
    SqlAlchemyAssignorRepository,
    SqlAlchemyExchangeRateRepository,
    SqlAlchemyProductTypeRepository,
    SqlAlchemyReceivableRepository,
    SqlAlchemySettlementRepository,
)
from srm_credit_engine.resilience import ResilientCurrencyConverter

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_assignor_repo(session: SessionDep) -> AssignorRepository:
    return SqlAlchemyAssignorRepository(session)


def get_product_type_repo(session: SessionDep) -> ProductTypeRepository:
    return SqlAlchemyProductTypeRepository(session)


def get_exchange_rate_repo(session: SessionDep) -> ExchangeRateRepository:
    return SqlAlchemyExchangeRateRepository(session)


def get_receivable_repo(session: SessionDep) -> ReceivableRepository:
    return SqlAlchemyReceivableRepository(session)


def get_settlement_repo(session: SessionDep) -> SettlementRepository:
    return SqlAlchemySettlementRepository(session)


def get_analytics_repo(session: SessionDep) -> AnalyticsRepository:
    return SqlAnalyticsRepository(session)


def get_currency_converter(
    rates: Annotated[ExchangeRateRepository, Depends(get_exchange_rate_repo)],
) -> CurrencyConverter:
    return ResilientCurrencyConverter(DatabaseCurrencyConverter(rates))


def get_pricing_service(
    converter: Annotated[CurrencyConverter, Depends(get_currency_converter)],
    settings: SettingsDep,
) -> PricingService:
    return PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=converter,
        base_rate_monthly=settings.base_rate_monthly,
    )


AssignorRepoDep = Annotated[AssignorRepository, Depends(get_assignor_repo)]
ProductTypeRepoDep = Annotated[ProductTypeRepository, Depends(get_product_type_repo)]
ExchangeRateRepoDep = Annotated[ExchangeRateRepository, Depends(get_exchange_rate_repo)]
ReceivableRepoDep = Annotated[ReceivableRepository, Depends(get_receivable_repo)]
SettlementRepoDep = Annotated[SettlementRepository, Depends(get_settlement_repo)]
PricingServiceDep = Annotated[PricingService, Depends(get_pricing_service)]
AnalyticsRepoDep = Annotated[AnalyticsRepository, Depends(get_analytics_repo)]
