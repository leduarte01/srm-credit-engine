import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createAssignor, listAssignors } from '../api/endpoints';
import { useI18n } from '../hooks/useI18n';
import type { AssignorCreate } from '../types/domain';

function NewAssignorModal({ onClose }: { onClose: () => void }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [document, setDocument] = useState('');
  const [legalName, setLegalName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (body: AssignorCreate) => createAssignor(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['assignors'] });
      onClose();
    },
    onError: (err: unknown) => {
      const msg = err instanceof Error ? err.message : 'Unexpected error';
      setError(msg);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate({ document, legal_name: legalName });
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-zinc-900">{t('assignor_form_title')}</h2>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">
              {t('assignor_form_document')}
            </label>
            <input
              type="text"
              required
              inputMode="numeric"
              pattern="[0-9]{11,14}"
              value={document}
              onChange={(e) => setDocument(e.target.value.replace(/\D/g, ''))}
              placeholder={t('assignor_form_document_placeholder')}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">
              {t('assignor_form_legal_name')}
            </label>
            <input
              type="text"
              required
              minLength={2}
              value={legalName}
              onChange={(e) => setLegalName(e.target.value)}
              placeholder={t('assignor_form_legal_name_placeholder')}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
            >
              {t('help_close')}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
            >
              {mutation.isPending ? t('assignor_form_submitting') : t('assignor_form_submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function AssignorsPage() {
  const { t } = useI18n();
  const [showModal, setShowModal] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['assignors'],
    queryFn: () => listAssignors(),
  });

  const assignors = data?.items ?? [];

  return (
    <div className="p-6">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">{t('assignors_title')}</h1>
          <p className="mt-1 text-sm text-zinc-500">{t('assignors_subtitle')}</p>
        </div>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        >
          {t('btn_new_assignor')}
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 bg-zinc-50 text-left">
              <th className="px-4 py-3 font-semibold text-zinc-700">
                {t('assignors_col_document')}
              </th>
              <th className="px-4 py-3 font-semibold text-zinc-700">
                {t('assignors_col_legal_name')}
              </th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={2} className="px-4 py-8 text-center text-zinc-400">
                  {t('assignors_loading')}
                </td>
              </tr>
            )}
            {!isLoading && assignors.length === 0 && (
              <tr>
                <td colSpan={2} className="px-4 py-8 text-center text-zinc-400">
                  {t('assignors_empty')}
                </td>
              </tr>
            )}
            {assignors.map((a) => (
              <tr key={a.document} className="border-t border-zinc-100 hover:bg-zinc-50">
                <td className="px-4 py-3 font-mono text-zinc-900">{a.document}</td>
                <td className="px-4 py-3 text-zinc-700">{a.legal_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && <NewAssignorModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
