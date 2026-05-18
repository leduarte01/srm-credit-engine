import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { KpiCards } from './KpiCards';
import * as queries from '../hooks/queries';

type UseReceivableStatsReturn = ReturnType<typeof queries.useReceivableStats>;

function makeResult(total: number, loading = false) {
  return {
    data: loading ? undefined : { items: [], meta: { total, offset: 0, limit: 1 } },
    isLoading: loading,
  } as unknown as UseReceivableStatsReturn['pending'];
}

describe('KpiCards', () => {
  it('renders status labels', () => {
    vi.spyOn(queries, 'useReceivableStats').mockReturnValue({
      pending: makeResult(0, true),
      settled: makeResult(0, true),
      cancelled: makeResult(0, true),
    });

    render(<KpiCards />);

    expect(screen.getByText('Total')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Settled')).toBeInTheDocument();
    expect(screen.getByText('Cancelled')).toBeInTheDocument();
  });

  it('renders counts and total when data is available', () => {
    vi.spyOn(queries, 'useReceivableStats').mockReturnValue({
      pending: makeResult(4),
      settled: makeResult(10),
      cancelled: makeResult(2),
    });

    render(<KpiCards />);

    expect(screen.getByText('16')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('shows zero total when all counts are zero', () => {
    vi.spyOn(queries, 'useReceivableStats').mockReturnValue({
      pending: makeResult(0),
      settled: makeResult(0),
      cancelled: makeResult(0),
    });

    render(<KpiCards />);

    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThanOrEqual(3);
  });
});
