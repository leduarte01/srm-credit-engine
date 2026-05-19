"""Infrastructure layer — DB, repositories, external gateways."""

from srm_credit_engine.infrastructure.database import (
    get_engine,
    get_session,
    get_sessionmaker,
    session_scope,
)
from srm_credit_engine.infrastructure.database_currency_converter import (
    DatabaseCurrencyConverter,
)
from srm_credit_engine.infrastructure.fallback_currency_converter import (
    FallbackCurrencyConverter,
)
from srm_credit_engine.infrastructure.live_rate_converter import (
    LiveRateCurrencyConverter,
)
from srm_credit_engine.infrastructure.models import Base
from srm_credit_engine.infrastructure.repositories import (
    SqlAlchemyAssignorRepository,
    SqlAlchemyExchangeRateRepository,
    SqlAlchemyProductTypeRepository,
    SqlAlchemyReceivableRepository,
    SqlAlchemySettlementRepository,
)

__all__ = [
    "Base",
    "DatabaseCurrencyConverter",
    "FallbackCurrencyConverter",
    "LiveRateCurrencyConverter",
    "SqlAlchemyAssignorRepository",
    "SqlAlchemyExchangeRateRepository",
    "SqlAlchemyProductTypeRepository",
    "SqlAlchemyReceivableRepository",
    "SqlAlchemySettlementRepository",
    "get_engine",
    "get_session",
    "get_sessionmaker",
    "session_scope",
]
