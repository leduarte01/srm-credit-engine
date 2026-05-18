import { useI18n } from '../hooks/useI18n';
import { useUiStore } from '../store/uiStore';

export function LanguageToggle() {
  const { lang } = useI18n();
  const setLang = useUiStore((s) => s.setLang);

  return (
    <div className="flex items-center rounded-md bg-zinc-800 p-0.5 text-xs font-semibold">
      <button
        type="button"
        aria-pressed={lang === 'pt'}
        onClick={() => setLang('pt')}
        className={
          lang === 'pt'
            ? 'rounded px-2 py-1 bg-zinc-100 text-zinc-900'
            : 'rounded px-2 py-1 text-zinc-400 hover:text-zinc-200'
        }
      >
        PT
      </button>
      <button
        type="button"
        aria-pressed={lang === 'en'}
        onClick={() => setLang('en')}
        className={
          lang === 'en'
            ? 'rounded px-2 py-1 bg-zinc-100 text-zinc-900'
            : 'rounded px-2 py-1 text-zinc-400 hover:text-zinc-200'
        }
      >
        EN
      </button>
    </div>
  );
}
