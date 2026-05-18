/**
 * Decimal-string-safe formatting helpers.
 *
 * The backend exchanges monetary amounts and rates as decimal strings to
 * preserve precision. We only convert to `Number` for the final user-facing
 * representation — never for arithmetic.
 */

export function formatMoney(amount: string, currency: string, locale = 'pt-BR'): string {
  const value = Number(amount);
  if (Number.isNaN(value)) return `${amount} ${currency}`;
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(value);
  } catch {
    return `${amount} ${currency}`;
  }
}

export function formatRatePercent(rate: string, fractionDigits = 4): string {
  const value = Number(rate);
  if (Number.isNaN(value)) return rate;
  return `${(value * 100).toFixed(fractionDigits)}%`;
}

export function formatDate(iso: string, locale = 'pt-BR'): string {
  // Accepts both `YYYY-MM-DD` and ISO timestamps; parse explicitly for the
  // date-only case so timezone offsets do not shift the displayed day.
  const dateOnly = /^\d{4}-\d{2}-\d{2}$/.test(iso);
  const date = dateOnly ? new Date(`${iso}T00:00:00`) : new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(date);
}
