# PR #12 — Frontend: operator panel with pricing simulator and receivables grid

## Summary
Introduces the React-based operator panel that consumes the FastAPI
backend over HTTP. Operators get a single-page dashboard to list and
filter receivables (TanStack Table + zustand store), simulate pricing
without persistence, and settle or cancel pending receivables. The
new `frontend/` workspace is self-contained: Vite 8, React 19,
TypeScript with strict project references, Tailwind v4 (CSS-only
config), TanStack Query for server cache, axios with a typed error
envelope, and Vitest + Testing Library for tests.

## Scope
- New `frontend/` workspace scaffolded with Vite + React 19 +
  TypeScript. Tailwind v4 via the `@tailwindcss/vite` plugin (no
  `tailwind.config.ts` — config lives in `src/index.css`).
- `vite.config.ts` — dev proxies `/api` → `http://localhost:8000` so
  the panel can run against the local backend without CORS plumbing.
  Vitest config split into `vitest.config.ts` to bridge the Vite 8 /
  Vite 6 type gap that Vitest 3 still carries.
- `src/api/`
  - `client.ts` — `createApiClient(baseURL)` factory + `apiClient`
    singleton. Reads `VITE_API_BASE_URL`, defaults to
    `http://localhost:8000/api/v1`. Response interceptor inspects
    backend `ErrorResponse {code, message, details}` payloads and
    rethrows an `ApiClientError` so consumers get a single error
    type to handle.
  - `endpoints.ts` — typed helpers for `listReceivables`,
    `getReceivable`, `cancelReceivable` (PATCH), `simulatePricing`
    and `settleReceivable`.
- `src/types/domain.ts` — domain DTOs mirroring the backend
  contracts. Monetary amounts stay as decimal strings end-to-end and
  are only parsed to `Number` for `Intl.NumberFormat` display.
- `src/lib/format.ts` — `formatMoney`, `formatRatePercent`,
  `formatDate`. The date helper detects ISO date-only strings and
  appends `T00:00:00` to avoid the UTC→local shift that drops the
  due-date by one day in negative-offset locales.
- `src/hooks/queries.ts` — TanStack Query wrappers:
  - `useReceivables(filters)` keyed by the active filter object.
  - `useSimulatePricing()` mutation (no cache invalidation —
    pricing is a pure simulation).
  - `useSettleReceivable()` / `useCancelReceivable()` mutations that
    invalidate the `['receivables']` cache so the grid refreshes
    on success.
- `src/store/uiStore.ts` — zustand store for filters (with
  pagination offset auto-reset to 0 on any filter change) and the
  currently selected receivable id.
- `src/components/`
  - `StatusBadge.tsx` — color-coded ring badge (amber/emerald/zinc).
  - `ReceivableTable.tsx` — TanStack Table 8 rendering columns for
    reference, assignor, product, face value, issue/due dates,
    status and per-row settle/cancel actions (only enabled when the
    status is `PENDING`).
  - `PricingSimulator.tsx` — controlled form posting to
    `/pricing/simulate`. Renders the full result envelope including
    optional FX rate.
  - `ReceivableFilters.tsx` — assignor/product/currency/status
    filters wired to the zustand store.
- `src/pages/DashboardPage.tsx` — composes everything plus a refetch
  button and a toast banner that surfaces last action feedback,
  including `ApiClientError.code + message` on failure.

## Quality gates
- **Typecheck** (`tsc -b --noEmit`): clean
- **Lint** (`eslint .`): clean
- **Vitest**: **13/13** passing (3 spec files)
- **Build** (`vite build`): 130 modules, 327.29 kB JS (101.72 kB
  gzipped), 15.79 kB CSS (3.86 kB gzipped)

## New tests
- `src/lib/format.test.ts` — 7 cases covering BRL/USD currency
  formatting, NaN/invalid fallback, percent rendering of rate
  decimals, ISO-date-only no-drift behaviour.
- `src/components/ReceivableTable.test.tsx` — 4 cases covering row
  rendering with R$ formatting, the gating of settle/cancel buttons
  by status, the settle callback invocation, and the empty-state
  fallback.
- `src/api/client.test.ts` — 2 cases covering the ApiClientError
  wrapping of backend `ErrorResponse` payloads and the pass-through
  of unrelated errors, via `axios-mock-adapter`.

## Architectural decisions
- **Decimal strings end-to-end for money**: the backend ships
  monetary fields as decimal strings to avoid IEEE-754 drift. The
  frontend mirrors that — `Money.amount: string` everywhere, and
  only `formatMoney` parses to `Number` for the very last display
  step. No arithmetic on the frontend.
- **Single `ApiClientError` type**: the response interceptor
  normalises every backend failure shape into one class, so each
  component / hook handles errors uniformly instead of branching on
  `axios.isAxiosError` + payload shape.
- **TanStack Query staleTime 30 s + manual refresh**: backend reads
  are idempotent and not high-frequency. A 30-second freshness
  window cuts redundant network chatter while still letting the
  operator force a refresh via the toolbar button.
- **Tailwind v4 CSS config**: Tailwind v4 drops the JS config file
  and reads directives from CSS. Keeps the project free of an
  ad-hoc `tailwind.config.ts` and aligns with the upstream
  recommendation.
- **Zustand filter store separated from server cache**: filters are
  UI state and belong in zustand; server data belongs in TanStack
  Query. The two communicate through query keys, so cache
  invalidation and filter resets stay orthogonal.
- **Split `vite.config.ts` / `vitest.config.ts`**: Vitest 3 still
  bundles its own Vite 6 instance, which conflicts with the
  workspace Vite 8 plugin types when the test block is colocated
  in `vite.config.ts`. Splitting keeps both type-clean.
- **Dev proxy instead of CORS for local runs**: Vite proxies
  `/api → :8000`, matching the contract used in production where
  the panel and the backend share an origin behind a reverse
  proxy.

## How to validate locally
```pwsh
cd frontend
npm install
npm run typecheck
npm run lint
npm run test
npm run build
npm run dev   # http://localhost:5173, expects backend on :8000
```
