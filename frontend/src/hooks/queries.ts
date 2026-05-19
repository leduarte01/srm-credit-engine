import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  cancelReceivable,
  createReceivable,
  listReceivables,
  settleReceivable,
  simulatePricing,
} from '../api/endpoints';
import type {
  PricingSimulateRequest,
  PricingSimulateResponse,
  Receivable,
  ReceivableCreate,
  ReceivableListFilters,
  ReceivableStatus,
  Settlement,
} from '../types/domain';

export const queryKeys = {
  receivables: (filters: ReceivableListFilters) => ['receivables', filters] as const,
};

export function useReceivables(filters: ReceivableListFilters) {
  return useQuery({
    queryKey: queryKeys.receivables(filters),
    queryFn: () => listReceivables(filters),
  });
}

export function useSimulatePricing() {
  return useMutation<PricingSimulateResponse, Error, PricingSimulateRequest>({
    mutationFn: simulatePricing,
  });
}

export function useCreateReceivable() {
  const qc = useQueryClient();
  return useMutation<Receivable, Error, ReceivableCreate>({
    mutationFn: createReceivable,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['receivables'] });
    },
  });
}

export function useSettleReceivable() {
  const qc = useQueryClient();
  return useMutation<Settlement, Error, { id: string; referenceDate?: string }>({
    mutationFn: ({ id, referenceDate }) => settleReceivable(id, referenceDate),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['receivables'] });
    },
  });
}

export function useCancelReceivable() {
  const qc = useQueryClient();
  return useMutation<Receivable, Error, string>({
    mutationFn: cancelReceivable,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['receivables'] });
    },
  });
}

const STAT_STATUSES = ['PENDING', 'SETTLED', 'CANCELLED'] as const;

export function useReceivableStats() {
  const results = useQueries({
    queries: STAT_STATUSES.map((status: ReceivableStatus) => ({
      queryKey: ['receivables', { status, limit: 1, offset: 0 }],
      queryFn: () => listReceivables({ status, limit: 1, offset: 0 }),
    })),
  });
  return {
    pending: results[0],
    settled: results[1],
    cancelled: results[2],
  };
}
