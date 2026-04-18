import { useI18n } from 'vue-i18n'
import type { SupportedLocale } from '@/i18n'

const LOCALE_KEY = 'app-locale'

export const supportedLocales: { value: SupportedLocale; label: string; flag: string }[] = [
  { value: 'zh-TW', label: '繁體中文', flag: '🇹🇼' },
  { value: 'en', label: 'English', flag: '🇺🇸' },
]

export function useLocale() {
  const { locale } = useI18n()

  function setLocale(lang: SupportedLocale) {
    locale.value = lang
    localStorage.setItem(LOCALE_KEY, lang)
    document.documentElement.lang = lang === 'en' ? 'en' : 'zh-Hant-TW'
  }

  return {
    locale,
    setLocale,
    supportedLocales,
  }
}
