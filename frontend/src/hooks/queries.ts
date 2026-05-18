import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  cancelReceivable,
  listReceivables,
  settleReceivable,
  simulatePricing,
} from '../api/endpoints';
import type {
  PricingSimulateRequest,
  PricingSimulateResponse,
  Receivable,
  ReceivableListFilters,
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
