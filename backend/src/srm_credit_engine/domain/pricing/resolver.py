"""Resolver/factory for pricing strategies keyed by product code."""

from __future__ import annotations

from collections.abc import Iterable
from typing import cast

from srm_credit_engine.domain.exceptions import PricingStrategyNotFoundError
from srm_credit_engine.domain.pricing.strategies import (
    ChequePreDatadoStrategy,
    ContratoUsdStrategy,
    DuplicataMercantilStrategy,
)
from srm_credit_engine.domain.pricing.strategy import PricingStrategy

_DEFAULT_STRATEGIES: tuple[PricingStrategy, ...] = cast(
    "tuple[PricingStrategy, ...]",
    (DuplicataMercantilStrategy, ChequePreDatadoStrategy, ContratoUsdStrategy),
)

class PricingStrategyResolver:
    """Registry that maps a product code to its pricing strategy.

    New product types can be registered at runtime via :meth:`register`,
    keeping the engine extensible without modifying existing strategies
    (Open/Closed Principle).
    """

    def __init__(self, strategies: Iterable[PricingStrategy] | None = None) -> None:
        self._registry: dict[str, PricingStrategy] = {}
        for strategy in strategies if strategies is not None else _DEFAULT_STRATEGIES:
            self.register(strategy)

    def register(self, strategy: PricingStrategy) -> None:
        self._registry[strategy.code] = strategy

    def resolve(self, product_code: str) -> PricingStrategy:
        try:
            return self._registry[product_code]
        except KeyError as exc:
            raise PricingStrategyNotFoundError(
                f"No pricing strategy registered for product '{product_code}'."
            ) from exc

    def available_codes(self) -> tuple[str, ...]:
        return tuple(self._registry.keys())
