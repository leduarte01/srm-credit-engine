import { useI18n } from '../hooks/useI18n';
import type { TranslationKey } from '../lib/i18n';
import type { ReceivableStatus } from '../types/domain';

const STYLES: Record<ReceivableStatus, string> = {
  PENDING: 'bg-amber-100 text-amber-800 ring-amber-200',
  SETTLED: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  CANCELLED: 'bg-zinc-200 text-zinc-700 ring-zinc-300',
};

const STATUS_LABEL_KEY: Record<ReceivableStatus, TranslationKey> = {
  PENDING: 'status_pending',
  SETTLED: 'status_settled',
  CANCELLED: 'status_cancelled',
};

interface Props {
  status: ReceivableStatus;
}

export function StatusBadge({ status }: Props) {
  const { t } = useI18n();
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STYLES[status]}`}
    >
      {t(STATUS_LABEL_KEY[status])}
    </span>
  );
}
