import { useState } from 'react';

import { ApiClientError } from '../api/client';
import { KpiCards } from '../components/KpiCards';
import { PricingSimulator } from '../components/PricingSimulator';
import { ReceivableFilters } from '../components/ReceivableFilters';
import { ReceivableTable } from '../components/ReceivableTable';
import { useI18n } from '../hooks/useI18n';
import { useCancelReceivable, useReceivables, useSettleReceivable } from '../hooks/queries';
import { useUiStore } from '../store/uiStore';
import type { Receivable } from '../types/domain';

export function DashboardPage() {
  const { t } = useI18n();
  const filters = useUiStore((s) => s.filters);
  const { data, isLoading, isError, error, refetch, isFetching } = useReceivables(filters);
  const settleMutation = useSettleReceivable();
  const cancelMutation = useCancelReceivable();
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ kind: 'ok' | 'error'; message: string } | null>(null);

  const runAction = async (
    receivable: Receivable,
    mutate: (id: string) => Promise<unknown>,
    successLabel: string,
  ) => {
    setPendingId(receivable.id);
    setFeedback(null);
    try {
      await mutate(receivable.id);
      setFeedback({ kind: 'ok', message: `${successLabel}: ${receivable.external_reference}` });
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? `${err.code}: ${err.message}`
          : err instanceof Error
            ? err.message
            : 'Unknown error';
      setFeedback({ kind: 'error', message });
    } finally {
      setPendingId(null);
    }
  };

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">{t('page_title')}</h1>
          <p className="text-sm text-zinc-600">{t('page_subtitle')}</p>
        </div>
        <button
          type="button"
          onClick={() => void refetch()}
          className="inline-flex items-center rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
          disabled={isFetching}
        >
          {isFetching ? t('btn_refreshing') : t('btn_refresh')}
        </button>
      </header>

      <KpiCards />

      <PricingSimulator />

      <section className="space-y-3">
        <ReceivableFilters />

        {feedback && (
          <p
            role="status"
            className={
              feedback.kind === 'ok'
                ? 'rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-700 ring-1 ring-inset ring-emerald-200'
                : 'rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 ring-1 ring-inset ring-rose-200'
            }
          >
            {feedback.message}
          </p>
        )}

        {isLoading && <p className="text-sm text-zinc-600">{t('loading_receivables')}</p>}

        {isError && (
          <p
            role="alert"
            className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 ring-1 ring-inset ring-rose-200"
          >
            {error instanceof ApiClientError
              ? `${error.code}: ${error.message}`
              : (error as Error).message}
          </p>
        )}

        {data && (
          <>
            <ReceivableTable
              data={data.items}
              pendingId={pendingId}
              onSettle={(r) =>
                void runAction(r, (id) => settleMutation.mutateAsync({ id }), 'Settled')
              }
              onCancel={(r) =>
                void runAction(r, (id) => cancelMutation.mutateAsync(id), 'Cancelled')
              }
            />
            <p className="text-xs text-zinc-500">
              {t('showing_x_of_y', { shown: data.items.length, total: data.meta.total })}
            </p>
          </>
        )}
      </section>
    </main>
  );
}
