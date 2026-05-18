import { useMemo } from 'react';
import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from '@tanstack/react-table';

import { useI18n } from '../hooks/useI18n';
import { formatDate, formatMoney } from '../lib/format';
import type { Receivable } from '../types/domain';
import { StatusBadge } from './StatusBadge';

interface Props {
  data: Receivable[];
  onSettle?: (receivable: Receivable) => void;
  onCancel?: (receivable: Receivable) => void;
  pendingId?: string | null;
}

export function ReceivableTable({ data, onSettle, onCancel, pendingId }: Props) {
  const { t, lang } = useI18n();

  const columns = useMemo<ColumnDef<Receivable>[]>(
    () => [
      {
        header: t('col_reference'),
        accessorKey: 'external_reference',
        cell: (info) => (
          <span className="font-mono text-xs text-zinc-700">{info.getValue<string>()}</span>
        ),
      },
      {
        header: t('col_assignor'),
        accessorKey: 'assignor_document',
        cell: (info) => (
          <span className="font-mono text-xs text-zinc-600">{info.getValue<string>()}</span>
        ),
      },
      {
        header: t('col_product'),
        accessorKey: 'product_code',
      },
      {
        header: t('col_face_value'),
        accessorFn: (row) => row.face_value,
        id: 'face_value',
        cell: (info) => {
          const m = info.getValue<Receivable['face_value']>();
          return <span className="font-medium">{formatMoney(m.amount, m.currency)}</span>;
        },
      },
      {
        header: t('col_issue'),
        accessorKey: 'issue_date',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        header: t('col_due'),
        accessorKey: 'due_date',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        header: t('col_status'),
        accessorKey: 'status',
        cell: (info) => <StatusBadge status={info.getValue<Receivable['status']>()} />,
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const r = row.original;
          if (r.status !== 'PENDING') return null;
          const busy = pendingId === r.id;
          return (
            <div className="flex justify-end gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => onSettle?.(r)}
                className="inline-flex items-center rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
              >
                {busy ? t('btn_settling') : t('btn_settle')}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => onCancel?.(r)}
                className="inline-flex items-center rounded-md bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-700 ring-1 ring-inset ring-zinc-300 hover:bg-zinc-200 disabled:opacity-50"
              >
                {t('btn_cancel')}
              </button>
            </div>
          );
        },
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [onSettle, onCancel, pendingId, lang],
  );

  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-zinc-200">
        <thead className="bg-zinc-50">
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => (
                <th
                  key={header.id}
                  scope="col"
                  className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-zinc-500"
                >
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-zinc-100 bg-white">
          {table.getRowModel().rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-3 py-6 text-center text-sm text-zinc-500">
                {t('no_receivables')}
              </td>
            </tr>
          ) : (
            table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-zinc-50">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="whitespace-nowrap px-3 py-2 text-sm text-zinc-700">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
