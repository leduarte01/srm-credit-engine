import type { ReceivableStatus } from '../types/domain';

const STYLES: Record<ReceivableStatus, string> = {
  PENDING: 'bg-amber-100 text-amber-800 ring-amber-200',
  SETTLED: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  CANCELLED: 'bg-zinc-200 text-zinc-700 ring-zinc-300',
};

interface Props {
  status: ReceivableStatus;
}

export function StatusBadge({ status }: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STYLES[status]}`}
    >
      {status}
    </span>
  );
}
