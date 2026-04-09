import { ref, watch } from 'vue'
import { useDark, useToggle } from '@vueuse/core'

/**
 * Standard shadcn/ui Theme Composable.
 * Manages dark mode, layout width, and color themes.
 */

export interface ThemeConfig {
  id: string
  label: string
  color: string
}

export const themes: ThemeConfig[] = [
  { id: 'zinc', label: 'Zinc', color: '#18181b' },
  { id: 'blue', label: 'Blue', color: '#3b82f6' },
  { id: 'violet', label: 'Violet', color: '#8b5cf6' },
  { id: 'rose', label: 'Rose', color: '#f43f5e' },
  { id: 'orange', label: 'Orange', color: '#f97316' },
  { id: 'green', label: 'Green', color: '#22c55e' },
]

export const surfaces = [
  { id: 'zinc', label: 'Zinc', color: '#71717a' },
  { id: 'slate', label: 'Slate', color: '#475569' },
  { id: 'gray', label: 'Gray', color: '#4b5563' },
  { id: 'neutral', label: 'Neutral', color: '#525252' },
  { id: 'stone', label: 'Stone', color: '#57534e' },
]

const THEME_STORAGE_KEY = 'app-color-theme'
const SURFACE_STORAGE_KEY = 'app-surface-theme'
const WIDTH_STORAGE_KEY = 'app-layout-width'

// Global state
const currentTheme = ref<string>(localStorage.getItem(THEME_STORAGE_KEY) || 'zinc')
const currentSurface = ref<string>(localStorage.getItem(SURFACE_STORAGE_KEY) || 'zinc')
const isNarrow = ref<boolean>(localStorage.getItem(WIDTH_STORAGE_KEY) === 'narrow')

export function useTheme() {
  const isDark = useDark()
  const toggleDark = useToggle(isDark)

  function toggleWidth() {
    isNarrow.value = !isNarrow.value
    localStorage.setItem(WIDTH_STORAGE_KEY, isNarrow.value ? 'narrow' : 'wide')
  }

  function setTheme(themeId: string) {
    currentTheme.value = themeId
    localStorage.setItem(THEME_STORAGE_KEY, themeId)
  }

  function setSurface(surfaceId: string) {
    currentSurface.value = surfaceId
    localStorage.setItem(SURFACE_STORAGE_KEY, surfaceId)
  }

  function applyTheme(theme: string, surface: string) {
    if (typeof window !== 'undefined') {
      const root = document.documentElement
      
      // Theme (Primary Color)
      if (theme && theme !== 'zinc') {
        root.setAttribute('data-theme', theme)
      } else {
        root.removeAttribute('data-theme')
      }

      // Surface (Neutral Colors)
      if (surface && surface !== 'zinc') {
        root.setAttribute('data-surface', surface)
      } else {
        root.removeAttribute('data-surface')
      }
    }
  }

  // Watch for changes and apply them
  watch([currentTheme, currentSurface], ([newTheme, newSurface]) => {
    applyTheme(newTheme, newSurface)
  }, { immediate: true })

  return {
    isDark,
    toggleDark,
    isNarrow,
    toggleWidth,
    themes,
    currentTheme,
    setTheme,
    surfaces,
    currentSurface,
    setSurface,
  }
}
