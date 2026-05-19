import { useState, type FormEvent } from 'react';

import { ApiClientError } from '../api/client';
import { useI18n } from '../hooks/useI18n';
import { useSimulatePricing } from '../hooks/queries';
import { formatMoney, formatRatePercent } from '../lib/format';
import type { PricingSimulateRequest } from '../types/domain';

const today = (): string => new Date().toISOString().slice(0, 10);
const addDays = (iso: string, days: number): string => {
  const d = new Date(`${iso}T00:00:00`);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

export function PricingSimulator() {
  const { t } = useI18n();
  const [productCode, setProductCode] = useState('DUPLICATA_MERCANTIL');
  const [amount, setAmount] = useState('10000.00');
  const [currency, setCurrency] = useState('BRL');
  const [issueDate, setIssueDate] = useState(today());
  const [dueDate, setDueDate] = useState(addDays(today(), 30));

  const mutation = useSimulatePricing();

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const body: PricingSimulateRequest = {
      product_code: productCode.trim(),
      face_value: { amount: amount.trim(), currency: currency.trim().toUpperCase() },
      issue_date: issueDate,
      due_date: dueDate,
    };
    mutation.mutate(body);
  };

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <header className="mb-4 flex items-baseline justify-between">
        <h2 className="text-base font-semibold text-zinc-900">{t('sim_title')}</h2>
        <p className="text-xs text-zinc-500">{t('sim_subtitle')}</p>
      </header>

      <form className="grid grid-cols-1 gap-3 sm:grid-cols-2" onSubmit={onSubmit}>
        <Field label={t('sim_product_code')}>
          <input
            value={productCode}
            onChange={(e) => setProductCode(e.target.value)}
            required
            className={inputClass}
          />
        </Field>
        <Field label={t('sim_currency')}>
          <input
            value={currency}
            maxLength={3}
            onChange={(e) => setCurrency(e.target.value.toUpperCase())}
            required
            className={inputClass}
          />
        </Field>
        <Field label={t('sim_face_value')}>
          <input
            value={amount}
            inputMode="decimal"
            onChange={(e) => setAmount(e.target.value)}
            required
            className={inputClass}
          />
        </Field>
        <Field label={t('sim_issue_date')}>
          <input
            type="date"
            value={issueDate}
            onChange={(e) => setIssueDate(e.target.value)}
            required
            className={inputClass}
          />
        </Field>
        <Field label={t('sim_due_date')}>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            required
            className={inputClass}
          />
        </Field>

        <div className="mt-2 flex justify-end sm:col-span-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="inline-flex items-center rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
          >
            {mutation.isPending ? t('sim_btn_simulating') : t('sim_btn_simulate')}
          </button>
        </div>
      </form>

      {mutation.isError && (
        <p
          role="alert"
          className="mt-4 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 ring-1 ring-inset ring-rose-200"
        >
          {mutation.error instanceof ApiClientError
            ? `${mutation.error.code}: ${mutation.error.message}`
            : mutation.error.message}
        </p>
      )}

      {mutation.data && (
        <dl className="mt-5 grid grid-cols-2 gap-3 rounded-md bg-zinc-50 p-4 text-sm sm:grid-cols-3">
          <Stat
            label={t('sim_present_value')}
            value={formatMoney(
              mutation.data.present_value.amount,
              mutation.data.present_value.currency,
            )}
          />
          <Stat
            label={t('sim_settlement_value')}
            value={formatMoney(
              mutation.data.settlement_value.amount,
              mutation.data.settlement_value.currency,
            )}
          />
          <Stat
            label={t('sim_eff_rate')}
            value={formatRatePercent(mutation.data.effective_monthly_rate)}
          />
          <Stat
            label={t('sim_base_rate')}
            value={formatRatePercent(mutation.data.base_rate_monthly)}
          />
          <Stat label={t('sim_spread')} value={formatRatePercent(mutation.data.spread_monthly)} />
          <Stat label={t('sim_term')} value={Number(mutation.data.term_months).toFixed(4)} />
          {mutation.data.fx_rate_applied && (
            <Stat label={t('sim_fx')} value={mutation.data.fx_rate_applied} />
          )}
        </dl>
      )}
    </section>
  );
}

const inputClass =
  'block w-full rounded-md border-0 px-3 py-1.5 text-sm text-zinc-900 ring-1 ring-inset ring-zinc-300 placeholder:text-zinc-400 focus:ring-2 focus:ring-inset focus:ring-zinc-900';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-zinc-600">{label}</span>
      {children}
    </label>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium text-zinc-500">{label}</dt>
      <dd className="mt-0.5 font-semibold text-zinc-900">{value}</dd>
    </div>
  );
}
