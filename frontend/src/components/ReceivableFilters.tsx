import { useUiStore } from '../store/uiStore';
import type { ReceivableStatus } from '../types/domain';

const STATUSES: ReceivableStatus[] = ['PENDING', 'SETTLED', 'CANCELLED'];

export function ReceivableFilters() {
  const filters = useUiStore((s) => s.filters);
  const setFilter = useUiStore((s) => s.setFilter);
  const setStatus = useUiStore((s) => s.setStatus);
  const reset = useUiStore((s) => s.resetFilters);

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
      <Field label="Assignor (document)">
        <input
          value={filters.assignor_document ?? ''}
          onChange={(e) => setFilter('assignor_document', e.target.value || undefined)}
          placeholder="Only digits"
          className={inputClass}
        />
      </Field>
      <Field label="Product">
        <input
          value={filters.product_code ?? ''}
          onChange={(e) => setFilter('product_code', e.target.value || undefined)}
          className={inputClass}
        />
      </Field>
      <Field label="Currency">
        <input
          value={filters.currency ?? ''}
          maxLength={3}
          onChange={(e) => setFilter('currency', e.target.value.toUpperCase() || undefined)}
          className={inputClass}
        />
      </Field>
      <Field label="Status">
        <select
          value={filters.status ?? ''}
          onChange={(e) => setStatus((e.target.value || undefined) as ReceivableStatus | undefined)}
          className={inputClass}
        >
          <option value="">Any</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </Field>
      <button
        type="button"
        onClick={reset}
        className="ml-auto inline-flex items-center rounded-md bg-zinc-100 px-3 py-1.5 text-xs font-medium text-zinc-700 ring-1 ring-inset ring-zinc-300 hover:bg-zinc-200"
      >
        Reset
      </button>
    </div>
  );
}

const inputClass =
  'block w-44 rounded-md border-0 px-3 py-1.5 text-sm text-zinc-900 ring-1 ring-inset ring-zinc-300 placeholder:text-zinc-400 focus:ring-2 focus:ring-inset focus:ring-zinc-900';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-zinc-600">{label}</span>
      {children}
    </label>
  );
}
