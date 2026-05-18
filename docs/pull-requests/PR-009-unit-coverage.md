# PR #9 — Unit coverage: property-based tests for domain invariants

## Summary
Strengthens the unit-test layer of the SRM Credit Engine with three new
test modules driven by **Hypothesis** property-based testing. Targets the
algebraic invariants of `Money`, the lifecycle of the `Receivable`
aggregate and the financial guarantees of every pricing strategy. Pushes
domain-package coverage to 100% and global coverage to **≈90%**.

## Scope
- `tests/unit/test_money_properties.py` — 13 property/example tests:
  - `Money + Money` is **commutative** and **associative** for any
    same-currency pair (`Decimal` strategy, up to 2 decimal places).
  - `subtract` inverts `add`.
  - `multiply(Decimal("1"))` is the identity; `multiply(Decimal("0"))`
    yields amount zero.
  - `quantize(places)` is **idempotent**.
  - Constructing with a lower-case currency normalises to upper-case.
  - Any cross-currency `add`/`subtract` raises `ValueError`.
  - Bankers’ rounding in `quantize(3)`; `__str__` includes amount and
    currency.
- `tests/unit/test_entity_invariants.py` — 22 tests:
  - **`Assignor`**: CNPJ punctuation stripping, short-document rejection,
    blank-name rejection.
  - **`Currency`**: invalid ISO-4217 length, negative `decimal_places`,
    upper-casing.
  - **`ProductType`**: rejects float spread, negative spread, blank code.
  - **`ExchangeRate`**: rejects float rate, non-positive rate, same base
    and quote currency, inverted `valid_to`. Validates the half-open
    `[valid_from, valid_to)` activity window — including the open-ended
    case.
  - **`Receivable`**: rejects `due_date ≤ issue_date`, blank
    `external_reference`, non-positive `face_value`; `term_in_months` is
    zero past the due date; full state-machine coverage
    (`PENDING → PRICED → SETTLED`, double-settle, cancel-after-settle,
    settle/price after cancel).
  - **Property-based state machine**: a random list of `price/settle/cancel`
    operations always leaves `version` exactly equal to the count of
    successful transitions.
  - **Property-based term**: any positive day-delta yields a strictly
    positive monthly term.
- `tests/unit/test_pricing_properties.py` — 14 tests:
  - For all three strategies (`DuplicataMercantilStrategy`,
    `ChequePreDatadoStrategy`, `ContratoUsdStrategy`):
    - **PV ≤ face_value** for any `(face, term, base_rate)`.
    - **PV > 0** for the same domain.
    - **effective_rate == base_rate + spread`** identity.
  - Strategy rejects float `term_months`/`base_rate_monthly` and negative
    values.
  - `PricingService` rejects a float `base_rate_monthly` at construction.
  - `PricingService.price` raises `ValueError("Product mismatch")` when
    `receivable.product_code != product.code`.
  - `PricingService.price` short-circuits the converter when receivable
    and product currencies match (asserts the converter is never invoked
    via a stub that would `AssertionError`).

## Quality gates
- **Ruff**: all checks passed
- **Mypy --strict**: 55 source files, no issues
- **Pytest**: **133/133** passing (was 84 before)
- **Coverage**: **90.03%** global (gate ≥80%)
  - `domain/entities/*` and `domain/value_objects/money.py`: **100%**
  - `domain/pricing/*` and `domain/services/pricing_service.py`: **100%**
  - `infrastructure/database_currency_converter.py`: **100%** (via
    integration suite, unchanged here)

## Architectural decisions
- **Hypothesis over hand-rolled examples**: the financial invariants
  exercised here (PV ≤ FV, `add` commutativity, version monotonicity)
  are *universally quantified* statements. Property-based testing
  expresses them directly instead of enumerating a finite — and biased —
  example set. Strategies cap `Decimal` ranges and decimal places to
  keep `Decimal ** Decimal` exponentiation well-conditioned and
  test-suite runtime negligible (~8 s end-to-end).
- **No production code changes**. This PR is purely a test-layer
  hardening pass; the domain modules were already correct and now
  carry executable proofs of their invariants.
- **Stub converter** (`_StubConverter`) is defined inline in
  `test_pricing_properties.py` rather than promoted to a fixture: it is
  used by exactly two tests and exists only to assert that the FX path
  is short-circuited for same-currency settlements.

## How to validate locally
```pwsh
cd backend
uv run pytest -q
uv run ruff check .
uv run mypy src
```
