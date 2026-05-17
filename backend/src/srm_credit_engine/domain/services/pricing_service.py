"""Pricing service — orchestrates Strategy + optional FX conversion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable
from srm_credit_engine.domain.ports.currency_converter import CurrencyConverter
from srm_credit_engine.domain.pricing.resolver import PricingStrategyResolver
from srm_credit_engine.domain.pricing.strategy import PricingResult
from srm_credit_engine.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class PricedReceivable:
    """Pricing result + final settlement amount in the product's currency."""

    pricing: PricingResult
    settlement_value: Money
    fx_rate_applied: Decimal | None


class PricingService:
    """Application-facing service that prices a receivable.

    Steps:
    1. Resolve the :class:`PricingStrategy` for the receivable's product.
    2. Compute the present value in the receivable's original currency.
    3. If the product settles in a different currency, convert via
       :class:`CurrencyConverter`. Otherwise return the PV unchanged.
    """

    def __init__(
        self,
        resolver: PricingStrategyResolver,
        currency_converter: CurrencyConverter,
        base_rate_monthly: Decimal,
    ) -> None:
        if not isinstance(base_rate_monthly, Decimal):
            raise TypeError("base_rate_monthly must be a decimal.Decimal.")
        self._resolver = resolver
        self._converter = currency_converter
        self._base_rate = base_rate_monthly

    async def price(
        self,
        receivable: Receivable,
        product: ProductType,
        reference_date: date,
        moment: datetime,
    ) -> PricedReceivable:
        if receivable.product_code != product.code:
            raise ValueError(
                f"Product mismatch: receivable={receivable.product_code} "
                f"product={product.code}"
            )

        strategy = self._resolver.resolve(receivable.product_code)
        term = receivable.term_in_months(reference_date)
        pricing = strategy.price(receivable.face_value, term, self._base_rate)

        if pricing.present_value.currency == product.settlement_currency_code:
            return PricedReceivable(
                pricing=pricing,
                settlement_value=pricing.present_value,
                fx_rate_applied=None,
            )

        converted = await self._converter.convert(
            pricing.present_value,
            product.settlement_currency_code,
            moment,
        )
        fx_rate = (converted.amount / pricing.present_value.amount).quantize(
            Decimal("0.000001")
        )
        return PricedReceivable(
            pricing=pricing,
            settlement_value=converted.quantize(2),
            fx_rate_applied=fx_rate,
        )
