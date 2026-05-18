import { useI18n } from '../hooks/useI18n';
import { useReceivableStats } from '../hooks/queries';
import type { TranslationKey } from '../lib/i18n';

const STATUS_CONFIG = {
  PENDING: {
    labelKey: 'kpi_pending' as TranslationKey,
    barColor: 'bg-amber-400',
    textColor: 'text-amber-700',
    cardBg: 'bg-amber-50',
    ring: 'ring-amber-200',
  },
  SETTLED: {
    labelKey: 'kpi_settled' as TranslationKey,
    barColor: 'bg-emerald-500',
    textColor: 'text-emerald-700',
    cardBg: 'bg-emerald-50',
    ring: 'ring-emerald-200',
  },
  CANCELLED: {
    labelKey: 'kpi_cancelled' as TranslationKey,
    barColor: 'bg-zinc-400',
    textColor: 'text-zinc-600',
    cardBg: 'bg-zinc-100',
    ring: 'ring-zinc-200',
  },
} as const;

export function KpiCards() {
  const { t } = useI18n();
  const { pending, settled, cancelled } = useReceivableStats();

  const counts = {
    PENDING: pending.data?.meta.total ?? 0,
    SETTLED: settled.data?.meta.total ?? 0,
    CANCELLED: cancelled.data?.meta.total ?? 0,
  } as const;

  const total = counts.PENDING + counts.SETTLED + counts.CANCELLED;
  const isLoading = pending.isLoading || settled.isLoading || cancelled.isLoading;

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {/* Total card */}
      <div className="rounded-xl bg-white px-4 py-5 ring-1 ring-inset ring-zinc-200">
        <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          {t('kpi_total')}
        </p>
        {isLoading ? (
          <div className="mt-2 h-8 w-10 animate-pulse rounded bg-zinc-200" />
        ) : (
          <p className="mt-1 text-3xl font-bold text-zinc-900">{total}</p>
        )}
      </div>

      {/* Per-status cards */}
      {(Object.keys(STATUS_CONFIG) as Array<keyof typeof STATUS_CONFIG>).map((status) => {
        const cfg = STATUS_CONFIG[status];
        const count = counts[status];
        const pct = total > 0 ? Math.round((count / total) * 100) : 0;
        const loading =
          status === 'PENDING'
            ? pending.isLoading
            : status === 'SETTLED'
              ? settled.isLoading
              : cancelled.isLoading;

        return (
          <div
            key={status}
            className={`rounded-xl px-4 py-5 ring-1 ring-inset ${cfg.cardBg} ${cfg.ring}`}
          >
            <p className={`text-xs font-semibold uppercase tracking-wider ${cfg.textColor}`}>
              {t(cfg.labelKey)}
            </p>
            {loading ? (
              <div className="mt-2 h-8 w-10 animate-pulse rounded bg-zinc-200" />
            ) : (
              <p className={`mt-1 text-3xl font-bold ${cfg.textColor}`}>{count}</p>
            )}
            {!loading && total > 0 && (
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-zinc-200">
                <div
                  className={`h-full rounded-full ${cfg.barColor}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
