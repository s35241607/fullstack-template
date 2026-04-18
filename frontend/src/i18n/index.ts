import { createI18n } from 'vue-i18n'
import en from './locales/en'
import zhTW from './locales/zh-TW'
import type { MessageSchema } from './locales/en'

export type SupportedLocale = 'en' | 'zh-TW'

const LOCALE_KEY = 'app-locale'

const savedLocale = (localStorage.getItem(LOCALE_KEY) as SupportedLocale) || 'zh-TW'

// Apply html lang attribute on initial load
document.documentElement.lang = savedLocale === 'en' ? 'en' : 'zh-Hant-TW'

export const i18n = createI18n<[MessageSchema], SupportedLocale>({
  legacy: false,          // Composition API mode
  globalInjection: true,  // Makes $t() available in all templates without calling useI18n()
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    'zh-TW': zhTW,
  },
})
