import { create } from 'zustand';

import type { Lang } from '../lib/i18n';
import type { ReceivableListFilters, ReceivableStatus } from '../types/domain';

interface UiState {
  filters: ReceivableListFilters;
  setFilter: <K extends keyof ReceivableListFilters>(
    key: K,
    value: ReceivableListFilters[K],
  ) => void;
  setOffset: (offset: number) => void;
  setStatus: (status: ReceivableStatus | undefined) => void;
  resetFilters: () => void;
  selectedReceivableId: string | null;
  selectReceivable: (id: string | null) => void;
  lang: Lang;
  setLang: (lang: Lang) => void;
}

const initialFilters: ReceivableListFilters = { offset: 0, limit: 50 };

function storedLang(): Lang {
  try {
    return localStorage.getItem('srm_lang') === 'pt' ? 'pt' : 'en';
  } catch {
    return 'en';
  }
}

export const useUiStore = create<UiState>((set) => ({
  filters: initialFilters,
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value, offset: 0 },
    })),
  setOffset: (offset) =>
    set((state) => ({
      filters: { ...state.filters, offset },
    })),
  setStatus: (status) =>
    set((state) => ({
      filters: { ...state.filters, status, offset: 0 },
    })),
  resetFilters: () => set({ filters: initialFilters }),
  selectedReceivableId: null,
  selectReceivable: (id) => set({ selectedReceivableId: id }),
  lang: storedLang(),
  setLang: (lang) => {
    try {
      localStorage.setItem('srm_lang', lang);
    } catch {
      /* ignore */
    }
    set({ lang });
  },
}));
