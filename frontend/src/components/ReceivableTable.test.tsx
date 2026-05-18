import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ReceivableTable } from './ReceivableTable';
import type { Receivable } from '../types/domain';

const pending: Receivable = {
  id: '11111111-1111-1111-1111-111111111111',
  assignor_document: '12345678901234',
  product_code: 'DUPL',
  face_value: { amount: '10000.00', currency: 'BRL' },
  issue_date: '2026-05-01',
  due_date: '2026-06-01',
  external_reference: 'REF-001',
  status: 'PENDING',
  version: 1,
};

const settled: Receivable = {
  ...pending,
  id: '22222222-2222-2222-2222-222222222222',
  external_reference: 'REF-002',
  status: 'SETTLED',
};

describe('<ReceivableTable />', () => {
  it('renders rows and formats face value as currency', () => {
    render(<ReceivableTable data={[pending, settled]} />);
    expect(screen.getByText('REF-001')).toBeInTheDocument();
    expect(screen.getByText('REF-002')).toBeInTheDocument();
    expect(screen.getAllByText(/R\$/)).toHaveLength(2);
  });

  it('shows actions only for PENDING rows', () => {
    render(<ReceivableTable data={[pending, settled]} />);
    // Only one Settle button (for the pending row).
    expect(screen.getAllByRole('button', { name: /settle/i })).toHaveLength(1);
  });

  it('invokes onSettle when the action is clicked', async () => {
    const onSettle = vi.fn();
    render(<ReceivableTable data={[pending]} onSettle={onSettle} />);
    await userEvent.click(screen.getByRole('button', { name: /settle/i }));
    expect(onSettle).toHaveBeenCalledWith(pending);
  });

  it('renders an empty state when no rows are passed', () => {
    render(<ReceivableTable data={[]} />);
    expect(screen.getByText(/no receivables match/i)).toBeInTheDocument();
  });
});
