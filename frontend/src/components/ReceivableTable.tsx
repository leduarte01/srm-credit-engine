import { useMemo } from 'react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from '@tanstack/react-table';

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
  const columns = useMemo<ColumnDef<Receivable>[]>(
    () => [
      {
        header: 'Reference',
        accessorKey: 'external_reference',
        cell: (info) => (
          <span className="font-mono text-xs text-zinc-700">{info.getValue<string>()}</span>
        ),
      },
      {
        header: 'Assignor',
        accessorKey: 'assignor_document',
        cell: (info) => (
          <span className="font-mono text-xs text-zinc-600">{info.getValue<string>()}</span>
        ),
      },
      {
        header: 'Product',
        accessorKey: 'product_code',
      },
      {
        header: 'Face value',
        accessorFn: (row) => row.face_value,
        id: 'face_value',
        cell: (info) => {
          const m = info.getValue<Receivable['face_value']>();
          return <span className="font-medium">{formatMoney(m.amount, m.currency)}</span>;
        },
      },
      {
        header: 'Issue',
        accessorKey: 'issue_date',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        header: 'Due',
        accessorKey: 'due_date',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        header: 'Status',
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
                {busy ? 'Settling…' : 'Settle'}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => onCancel?.(r)}
                className="inline-flex items-center rounded-md bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-700 ring-1 ring-inset ring-zinc-300 hover:bg-zinc-200 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          );
        },
      },
    ],
    [onSettle, onCancel, pendingId],
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
                No receivables match the current filters.
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
