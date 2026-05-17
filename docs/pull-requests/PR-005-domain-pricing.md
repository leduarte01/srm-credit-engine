# PR #5 — Domain entities + Pricing Strategy

## Summary
Implements the financial core of the SRM Credit Engine:
- All domain entities (Currency, ProductType, Assignor, ExchangeRate, Receivable, Settlement)
- Strategy Pattern for pricing (3 products with distinct monthly spreads)
- Currency converter outbound port (hexagonal architecture)
- `PricingService` orchestrating pricing + optional cross-currency settlement

## Files
- `backend/src/srm_credit_engine/domain/entities/*` — 6 entities + aggregate roots
- `backend/src/srm_credit_engine/domain/pricing/{strategy,strategies,resolver}.py`
- `backend/src/srm_credit_engine/domain/ports/currency_converter.py`
- `backend/src/srm_credit_engine/domain/services/pricing_service.py`
- `backend/tests/unit/test_{entities,pricing_strategies,pricing_service}.py`

## Highlights
- **Decimal everywhere** — `float` is rejected at every boundary (`Money`, `ProductType.monthly_spread`, `PricingStrategy.price` args).
- **Banker's rounding** (`ROUND_HALF_EVEN`) for all monetary quantisation.
- **Optimistic locking**: `Receivable.version` + `Settlement.version` increment on every state transition.
- **Audit trail**: `SettlementEvent` immutable records appended to `Settlement.events`.
- **Open/Closed**: new product types register via `PricingStrategyResolver.register()` without touching existing strategies.
- **Temporal FX validity** with half-open `[valid_from, valid_to)` window on `ExchangeRate`.
- **30-day month convention** on `Receivable.term_in_months` matching Brazilian receivables practice.
- **State machine guards** on `Receivable`: cannot settle twice, cannot price a cancelled receivable, etc.

## Validation (local)
- `uv run ruff check .` → clean
- `uv run mypy src` → 24 files, no issues (strict mode)
- `uv run pytest` → **39/39 passed, 83.63% coverage** (above 80% gate)

## Commits
- `feat(domain): add Currency, ProductType, Assignor and ExchangeRate entities`
- `feat(domain): add Receivable aggregate with optimistic locking and state machine`
- `feat(domain): add Settlement aggregate and immutable SettlementEvent log`
- `feat(pricing): add PricingStrategy protocol and PricingResult DTO`
- `feat(pricing): implement Duplicata, Cheque and ContratoUsd strategies`
- `feat(pricing): add PricingStrategyResolver registry (Open/Closed)`
- `feat(domain): add CurrencyConverter port and PricingService orchestrator`
- `test(domain): cover all entities, strategies and pricing service flows`
