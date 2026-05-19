import { type FormEvent, useState } from 'react';

import { ApiClientError } from '../api/client';
import { useCreateReceivable } from '../hooks/queries';
import { useI18n } from '../hooks/useI18n';

interface Props {
  onClose: () => void;
  onCreated: (reference: string) => void;
}

const inputClass =
  'block w-full rounded-md border-0 bg-white px-3 py-1.5 text-sm text-zinc-900 ring-1 ring-inset ring-zinc-300 placeholder:text-zinc-400 focus:ring-2 focus:ring-inset focus:ring-zinc-900';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-zinc-600">{label}</span>
      {children}
    </label>
  );
}

export function NewReceivableModal({ onClose, onCreated }: Props) {
  const { t } = useI18n();
  const mutation = useCreateReceivable();

  const [assignorDoc, setAssignorDoc] = useState('');
  const [productCode, setProductCode] = useState('DUPLICATA_MERCANTIL');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('BRL');
  const [issueDate, setIssueDate] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [reference, setReference] = useState('');
  const [fieldError, setFieldError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFieldError(null);
    try {
      const created = await mutation.mutateAsync({
        assignor_document: assignorDoc.replace(/\D/g, ''),
        product_code: productCode,
        face_value: { amount: amount.trim(), currency },
        issue_date: issueDate,
        due_date: dueDate,
        external_reference: reference.trim(),
      });
      onCreated(created.external_reference);
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? `${err.code}: ${err.message}`
          : err instanceof Error
            ? err.message
            : 'Unknown error';
      setFieldError(msg);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h2 className="text-base font-semibold text-zinc-900">{t('modal_new_title')}</h2>
        </div>

        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4 px-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Field label={t('modal_field_assignor_doc')}>
                <input
                  value={assignorDoc}
                  onChange={(e) => setAssignorDoc(e.target.value)}
                  placeholder="00000000000"
                  required
                  className={inputClass}
                />
              </Field>
            </div>

            <div className="col-span-2">
              <Field label={t('modal_field_product')}>
                <select
                  value={productCode}
                  onChange={(e) => setProductCode(e.target.value)}
                  required
                  className={inputClass}
                >
                  <option value="DUPLICATA_MERCANTIL">
                    Duplicata Mercantil — spread 1.5% a.m.
                  </option>
                  <option value="CHEQUE_PRE_DATADO">Cheque Pré-datado — spread 2.5% a.m.</option>
                  <option value="CONTRATO_USD">Contrato USD — spread 1.2% a.m.</option>
                </select>
              </Field>
            </div>

            <Field label={t('modal_field_amount')}>
              <input
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                inputMode="decimal"
                placeholder="10000.00"
                required
                className={inputClass}
              />
            </Field>

            <Field label={t('modal_field_currency')}>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                required
                className={inputClass}
              >
                <option value="BRL">BRL</option>
                <option value="USD">USD</option>
              </select>
            </Field>

            <Field label={t('modal_field_issue')}>
              <input
                type="date"
                value={issueDate}
                onChange={(e) => setIssueDate(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            <Field label={t('modal_field_due')}>
              <input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            <div className="col-span-2">
              <Field label={t('modal_field_reference')}>
                <input
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  placeholder="NF-0001"
                  required
                  className={inputClass}
                />
              </Field>
            </div>
          </div>

          {fieldError && (
            <p
              role="alert"
              className="rounded-md bg-rose-50 px-3 py-2 text-xs text-rose-700 ring-1 ring-inset ring-rose-200"
            >
              {fieldError}
            </p>
          )}

          <div className="flex justify-end gap-2 border-t border-zinc-200 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md px-4 py-1.5 text-sm font-medium text-zinc-700 ring-1 ring-inset ring-zinc-300 hover:bg-zinc-50"
            >
              {t('modal_btn_cancel')}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-md bg-zinc-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
            >
              {mutation.isPending ? t('modal_creating') : t('modal_btn_submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
