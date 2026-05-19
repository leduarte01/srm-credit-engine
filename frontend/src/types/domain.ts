/**
 * Domain types mirroring the FastAPI schemas exposed at /api/v1.
 *
 * Monetary amounts are exchanged as strings to preserve decimal precision
 * end-to-end. Convert to `number` only at presentation time, never in
 * arithmetic paths.
 */

export type ReceivableStatus = 'PENDING' | 'SETTLED' | 'CANCELLED';

export interface Money {
  amount: string;
  currency: string;
}

export interface Receivable {
  id: string;
  assignor_document: string;
  product_code: string;
  face_value: Money;
  issue_date: string;
  due_date: string;
  external_reference: string;
  status: ReceivableStatus;
  version: number;
}

export interface PageMeta {
  total: number;
  offset: number;
  limit: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

export interface PricingSimulateRequest {
  product_code: string;
  face_value: Money;
  issue_date: string;
  due_date: string;
  reference_date?: string | null;
}

export interface PricingSimulateResponse {
  product_code: string;
  present_value: Money;
  settlement_value: Money;
  base_rate_monthly: string;
  spread_monthly: string;
  effective_monthly_rate: string;
  term_months: string;
  fx_rate_applied: string | null;
}

export interface SettlementEvent {
  id: string;
  event_type: string;
  occurred_at: string;
  actor: string;
  payload: Record<string, unknown>;
}

export interface Settlement {
  id: string;
  receivable_id: string;
  discounted_value: Money;
  settlement_currency: string;
  settled_at: string;
  base_rate_monthly: string;
  spread_monthly: string;
  term_months: string;
  fx_rate_applied: string | null;
  version: number;
  events: SettlementEvent[];
}

export interface Assignor {
  document: string;
  legal_name: string;
}

export interface AssignorCreate {
  document: string;
  legal_name: string;
}

export interface ExchangeRate {
  base_currency: string;
  quote_currency: string;
  rate: string;
  valid_from: string;
  valid_to: string | null;
}

export interface ExchangeRateCreate {
  base_currency: string;
  quote_currency: string;
  rate: string;
  valid_from: string;
  valid_to?: string | null;
}

export interface ApiError {
  code: string;
  message: string;
  details?: { field?: string; message?: string }[] | null;
}

export interface ReceivableListFilters {
  assignor_document?: string;
  product_code?: string;
  status?: ReceivableStatus;
  currency?: string;
  due_from?: string;
  due_to?: string;
  offset?: number;
  limit?: number;
}
