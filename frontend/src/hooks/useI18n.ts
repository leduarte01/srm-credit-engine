import { TRANSLATIONS, type TranslationKey } from '../lib/i18n';
import { useUiStore } from '../store/uiStore';

export function useI18n() {
  const lang = useUiStore((s) => s.lang);
  const dict = TRANSLATIONS[lang];

  function t(key: TranslationKey, vars?: Record<string, string | number>): string {
    let str: string = dict[key] as string;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        str = str.replace(`{${k}}`, String(v));
      }
    }
    return str;
  }

  return { t, lang };
}
