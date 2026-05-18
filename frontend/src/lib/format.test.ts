import { describe, expect, it } from 'vitest';

import { formatDate, formatMoney, formatRatePercent } from './format';

describe('formatMoney', () => {
  it('formats BRL amounts with Brazilian locale', () => {
    const formatted = formatMoney('1234.56', 'BRL');
    expect(formatted).toMatch(/1\.234,56/);
    expect(formatted).toMatch(/R\$/);
  });

  it('formats USD amounts', () => {
    expect(formatMoney('1000.00', 'USD', 'en-US')).toBe('$1,000.00');
  });

  it('falls back gracefully when the amount is not numeric', () => {
    expect(formatMoney('not-a-number', 'BRL')).toBe('not-a-number BRL');
  });
});

describe('formatRatePercent', () => {
  it('renders a decimal rate as a percentage', () => {
    expect(formatRatePercent('0.015', 2)).toBe('1.50%');
  });

  it('returns the original input on parse failure', () => {
    expect(formatRatePercent('abc')).toBe('abc');
  });
});

describe('formatDate', () => {
  it('parses date-only inputs without timezone drift', () => {
    expect(formatDate('2026-05-18', 'en-US')).toMatch(/May 18, 2026/);
  });

  it('returns the original string on invalid input', () => {
    expect(formatDate('not-a-date')).toBe('not-a-date');
  });
});
