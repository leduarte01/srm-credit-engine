import { apiClient } from './client';
import type {
  Page,
  PricingSimulateRequest,
  PricingSimulateResponse,
  Receivable,
  ReceivableListFilters,
  Settlement,
} from '../types/domain';

export async function listReceivables(filters: ReceivableListFilters = {}): Promise<Page<Receivable>> {
  const params: Record<string, string | number> = {};
  if (filters.assignor_document) params.assignor_document = filters.assignor_document;
  if (filters.product_code) params.product_code = filters.product_code;
  if (filters.status) params.status = filters.status;
  if (filters.currency) params.currency = filters.currency;
  if (filters.due_from) params.due_from = filters.due_from;
  if (filters.due_to) params.due_to = filters.due_to;
  params.offset = filters.offset ?? 0;
  params.limit = filters.limit ?? 50;

  const { data } = await apiClient.get<Page<Receivable>>('/receivables', { params });
  return data;
}

export async function getReceivable(id: string): Promise<Receivable> {
  const { data } = await apiClient.get<Receivable>(`/receivables/${id}`);
  return data;
}

export async function cancelReceivable(id: string): Promise<Receivable> {
  const { data } = await apiClient.patch<Receivable>(`/receivables/${id}/cancel`);
  return data;
}

export async function simulatePricing(
  body: PricingSimulateRequest,
): Promise<PricingSimulateResponse> {
  const { data } = await apiClient.post<PricingSimulateResponse>('/pricing/simulate', body);
  return data;
}

export async function settleReceivable(
  receivableId: string,
  referenceDate?: string,
): Promise<Settlement> {
  const { data } = await apiClient.post<Settlement>('/settlements', {
    receivable_id: receivableId,
    reference_date: referenceDate ?? null,
  });
  return data;
}
