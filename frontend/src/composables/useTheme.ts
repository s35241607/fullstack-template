import { ref, watch } from 'vue'
import { useDark } from '@vueuse/core'

export type ThemeColor = 'slate' | 'blue' | 'violet' | 'rose' | 'amber' | 'teal'

export interface ThemeDef {
  id: ThemeColor
  label: string
  color: string // preview swatch hex
}

export const THEMES: ThemeDef[] = [
  { id: 'slate', label: 'Slate', color: '#64748b' },
  { id: 'blue', label: 'Blue', color: '#3b82f6' },
  { id: 'violet', label: 'Violet', color: '#8b5cf6' },
  { id: 'rose', label: 'Rose', color: '#f43f5e' },
  { id: 'amber', label: 'Amber', color: '#f59e0b' },
  { id: 'teal', label: 'Teal', color: '#14b8a6' },
]

const STORAGE_KEY = 'app-theme-color'
const WIDTH_STORAGE_KEY = 'app-layout-width'

const currentTheme = ref<ThemeColor>(
  (localStorage.getItem(STORAGE_KEY) as ThemeColor) ?? 'slate',
)
const isNarrow = ref<boolean>(localStorage.getItem(WIDTH_STORAGE_KEY) === 'narrow')

function applyTheme(theme: ThemeColor) {
  const root = document.documentElement
  // Remove all theme data attrs
  THEMES.forEach((t) => root.removeAttribute(`data-theme-${t.id}`))
  if (theme !== 'slate') {
    root.setAttribute(`data-theme`, theme)
  } else {
    root.removeAttribute('data-theme')
  }
}

// Apply on load
applyTheme(currentTheme.value)

watch(currentTheme, (val) => {
  applyTheme(val)
  localStorage.setItem(STORAGE_KEY, val)
})

watch(isNarrow, (val) => {
  localStorage.setItem(WIDTH_STORAGE_KEY, val ? 'narrow' : 'wide')
})

export function useTheme() {
  const dark = useDark()

  function setTheme(theme: ThemeColor) {
    currentTheme.value = theme
  }

  function toggleWidth() {
    isNarrow.value = !isNarrow.value
  }

  return {
    currentTheme,
    isNarrow,
    themes: THEMES,
    setTheme,
    toggleWidth,
    isDark: dark,
  }
}
