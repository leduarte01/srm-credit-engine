import { create } from 'zustand';

import type { ReceivableListFilters, ReceivableStatus } from '../types/domain';

interface UiState {
  filters: ReceivableListFilters;
  setFilter: <K extends keyof ReceivableListFilters>(
    key: K,
    value: ReceivableListFilters[K],
  ) => void;
  setStatus: (status: ReceivableStatus | undefined) => void;
  resetFilters: () => void;
  selectedReceivableId: string | null;
  selectReceivable: (id: string | null) => void;
}

const initialFilters: ReceivableListFilters = { offset: 0, limit: 50 };

export const useUiStore = create<UiState>((set) => ({
  filters: initialFilters,
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value, offset: 0 },
    })),
  setStatus: (status) =>
    set((state) => ({
      filters: { ...state.filters, status, offset: 0 },
    })),
  resetFilters: () => set({ filters: initialFilters }),
  selectedReceivableId: null,
  selectReceivable: (id) => set({ selectedReceivableId: id }),
}));
