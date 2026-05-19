import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createFxRate, listFxRates } from '../api/endpoints';
import { useI18n } from '../hooks/useI18n';
import type { ExchangeRateCreate } from '../types/domain';

const PAIRS: { base: string; quote: string }[] = [
  { base: 'USD', quote: 'BRL' },
  { base: 'BRL', quote: 'USD' },
];

function NewFxRateModal({ onClose }: { onClose: () => void }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [base, setBase] = useState('USD');
  const [quote, setQuote] = useState('BRL');
  const [rate, setRate] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validTo, setValidTo] = useState('');
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (body: ExchangeRateCreate) => createFxRate(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['fx-rates'] });
      onClose();
    },
    onError: (err: unknown) => {
      const msg = err instanceof Error ? err.message : 'Unexpected error';
      setError(msg);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const body: ExchangeRateCreate = {
      base_currency: base,
      quote_currency: quote,
      rate,
      valid_from: validFrom,
      valid_to: validTo || null,
    };
    mutation.mutate(body);
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-zinc-900">{t('fx_form_title')}</h2>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                {t('fx_form_base')}
              </label>
              <select
                value={base}
                onChange={(e) => setBase(e.target.value)}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              >
                <option value="USD">USD</option>
                <option value="BRL">BRL</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                {t('fx_form_quote')}
              </label>
              <select
                value={quote}
                onChange={(e) => setQuote(e.target.value)}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              >
                <option value="BRL">BRL</option>
                <option value="USD">USD</option>
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">
              {t('fx_form_rate')}
            </label>
            <input
              type="number"
              required
              step="0.000001"
              min="0.000001"
              value={rate}
              onChange={(e) => setRate(e.target.value)}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">
              {t('fx_form_valid_from')}
            </label>
            <input
              type="datetime-local"
              required
              value={validFrom}
              onChange={(e) => setValidFrom(e.target.value)}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">
              {t('fx_form_valid_to')}
            </label>
            <input
              type="datetime-local"
              value={validTo}
              onChange={(e) => setValidTo(e.target.value)}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
            >
              {t('help_close')}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
            >
              {mutation.isPending ? t('fx_form_submitting') : t('fx_form_submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function ExchangeRatesPage() {
  const { t } = useI18n();
  const [showModal, setShowModal] = useState(false);
  const [selectedPair, setSelectedPair] = useState<{ base: string; quote: string }>(PAIRS[0]);

  const { data: rates, isLoading } = useQuery({
    queryKey: ['fx-rates', selectedPair.base, selectedPair.quote],
    queryFn: () => listFxRates(selectedPair.base, selectedPair.quote),
  });

  return (
    <div className="p-6">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">{t('fx_title')}</h1>
          <p className="mt-1 text-sm text-zinc-500">{t('fx_subtitle')}</p>
        </div>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        >
          {t('btn_new_fx_rate')}
        </button>
      </div>

      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm font-medium text-zinc-700">{t('fx_pair_label')}</label>
        <div className="flex gap-2">
          {PAIRS.map((p) => (
            <button
              key={`${p.base}-${p.quote}`}
              type="button"
              onClick={() => setSelectedPair(p)}
              className={
                selectedPair.base === p.base && selectedPair.quote === p.quote
                  ? 'rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white'
                  : 'rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-50'
              }
            >
              {p.base}/{p.quote}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 bg-zinc-50 text-left">
              <th className="px-4 py-3 font-semibold text-zinc-700">{t('fx_col_pair')}</th>
              <th className="px-4 py-3 font-semibold text-zinc-700">{t('fx_col_rate')}</th>
              <th className="px-4 py-3 font-semibold text-zinc-700">{t('fx_col_valid_from')}</th>
              <th className="px-4 py-3 font-semibold text-zinc-700">{t('fx_col_valid_to')}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-zinc-400">
                  {t('fx_loading')}
                </td>
              </tr>
            )}
            {!isLoading && (!rates || rates.length === 0) && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-zinc-400">
                  {t('fx_empty')}
                </td>
              </tr>
            )}
            {rates?.map((r, i) => (
              <tr key={i} className="border-t border-zinc-100 hover:bg-zinc-50">
                <td className="px-4 py-3 font-medium text-zinc-900">
                  {r.base_currency}/{r.quote_currency}
                </td>
                <td className="px-4 py-3 font-mono text-zinc-900">{r.rate}</td>
                <td className="px-4 py-3 text-zinc-600">
                  {new Date(r.valid_from).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-zinc-600">
                  {r.valid_to ? (
                    new Date(r.valid_to).toLocaleString()
                  ) : (
                    <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                      {t('fx_col_open')}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && <NewFxRateModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
