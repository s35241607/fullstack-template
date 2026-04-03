import { ref } from 'vue'

// Global counter for in-flight requests
const pendingCount = ref(0)
// Top bar progress
const progress = ref(0)
let progressTimer: ReturnType<typeof setInterval> | null = null

function startProgress() {
  progress.value = 0
  if (progressTimer) clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    // Ease up to 85% while loading
    if (progress.value < 85) {
      progress.value += (85 - progress.value) * 0.12
    }
  }, 80)
}

function finishProgress() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  progress.value = 100
  setTimeout(() => {
    progress.value = 0
  }, 400)
}

export function useGlobalLoading() {
  const isGlobalLoading = ref(false)

  /**
   * Wraps an async function and tracks global loading state.
   */
  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    pendingCount.value++
    if (pendingCount.value === 1) {
      isGlobalLoading.value = true
      startProgress()
    }
    try {
      return await fn()
    } finally {
      pendingCount.value = Math.max(0, pendingCount.value - 1)
      if (pendingCount.value === 0) {
        isGlobalLoading.value = false
        finishProgress()
      }
    }
  }

  return {
    isGlobalLoading,
    pendingCount,
    progress,
    withLoading,
  }
}
