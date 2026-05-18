"""Tests for the PricingService — orchestration of strategy + FX."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from srm_credit_engine.domain.entities.product_type import ProductType
from srm_credit_engine.domain.entities.receivable import Receivable
from srm_credit_engine.domain.pricing.resolver import PricingStrategyResolver
from srm_credit_engine.domain.services.pricing_service import PricingService
from srm_credit_engine.domain.value_objects.money import Money


class _FakeConverter:
    """Deterministic stub for the CurrencyConverter port."""

    def __init__(self, rate: Decimal, target: str) -> None:
        self.rate = rate
        self.target = target
        self.calls: list[tuple[Money, str, datetime]] = []

    async def convert(self, amount: Money, target_currency: str, at: datetime) -> Money:
        self.calls.append((amount, target_currency, at))
        return Money(amount.amount * self.rate, target_currency)


def _make_receivable(product_code: str, currency: str) -> Receivable:
    issue = date(2025, 1, 1)
    return Receivable(
        assignor_document="12345678000190",
        product_code=product_code,
        face_value=Money(Decimal("1000.00"), currency),
        issue_date=issue,
        due_date=issue + timedelta(days=30),
        external_reference="NF-1",
    )


async def test_same_currency_skips_conversion() -> None:
    converter = _FakeConverter(rate=Decimal("5.0"), target="BRL")
    service = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=converter,
        base_rate_monthly=Decimal("0.01"),
    )
    product = ProductType(
        code="DUPLICATA_MERCANTIL",
        name="Duplicata",
        monthly_spread=Decimal("0.015"),
        settlement_currency_code="BRL",
    )
    receivable = _make_receivable("DUPLICATA_MERCANTIL", "BRL")

    result = await service.price(
        receivable, product, date(2025, 1, 1), datetime(2025, 1, 1, tzinfo=UTC)
    )

    assert result.fx_rate_applied is None
    assert result.settlement_value.currency == "BRL"
    assert converter.calls == []


async def test_cross_currency_applies_converter() -> None:
    # Receivable issued in USD, product settles in BRL — must convert.
    converter = _FakeConverter(rate=Decimal("5.0500"), target="BRL")
    service = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=converter,
        base_rate_monthly=Decimal("0.01"),
    )
    product = ProductType(
        code="CONTRATO_USD",
        name="Contrato USD",
        monthly_spread=Decimal("0.012"),
        settlement_currency_code="BRL",
    )
    receivable = _make_receivable("CONTRATO_USD", "USD")

    moment = datetime(2025, 1, 1, 12, tzinfo=UTC)
    result = await service.price(receivable, product, date(2025, 1, 1), moment)

    assert result.settlement_value.currency == "BRL"
    assert result.fx_rate_applied is not None
    assert result.fx_rate_applied == Decimal("5.050000")
    assert len(converter.calls) == 1
    assert converter.calls[0][1] == "BRL"
    assert converter.calls[0][2] == moment


async def test_product_mismatch_rejected() -> None:
    service = PricingService(
        resolver=PricingStrategyResolver(),
        currency_converter=_FakeConverter(Decimal("1"), "BRL"),
        base_rate_monthly=Decimal("0.01"),
    )
    product = ProductType(
        code="OTHER",
        name="x",
        monthly_spread=Decimal("0.01"),
        settlement_currency_code="BRL",
    )
    receivable = _make_receivable("DUPLICATA_MERCANTIL", "BRL")
    with pytest.raises(ValueError, match="Product mismatch"):
        await service.price(receivable, product, date(2025, 1, 1), datetime(2025, 1, 1, tzinfo=UTC))
