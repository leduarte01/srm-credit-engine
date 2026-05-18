import { useI18n } from '../hooks/useI18n';

interface Props {
  open: boolean;
  onClose: () => void;
}

interface SectionProps {
  title: string;
  body: string;
}

function HelpSection({ title, body }: SectionProps) {
  return (
    <div className="rounded-lg bg-zinc-50 px-4 py-3">
      <h3 className="text-sm font-semibold text-zinc-900">{title}</h3>
      <p className="mt-1 text-sm text-zinc-600">{body}</p>
    </div>
  );
}

export function HelpModal({ open, onClose }: Props) {
  const { t } = useI18n();

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div aria-hidden="true" className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Panel */}
      <div className="relative z-10 w-full max-w-lg overflow-hidden rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-4">
          <h2 className="text-base font-semibold text-zinc-900">{t('help_title')}</h2>
          <button
            type="button"
            aria-label={t('help_close')}
            onClick={onClose}
            className="rounded-md p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="h-5 w-5"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-3 overflow-y-auto p-5" style={{ maxHeight: '70vh' }}>
          <HelpSection title={t('help_kpi_title')} body={t('help_kpi_body')} />
          <HelpSection title={t('help_sim_title')} body={t('help_sim_body')} />
          <HelpSection title={t('help_filters_title')} body={t('help_filters_body')} />
          <HelpSection title={t('help_table_title')} body={t('help_table_body')} />
        </div>

        <div className="border-t border-zinc-200 px-5 py-3 text-right">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
          >
            {t('help_close')}
          </button>
        </div>
      </div>
    </div>
  );
}
