import { ref, shallowRef } from 'vue'

export interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'default' | 'destructive'
}

// ── Singleton module-level state ─────────────────────────────────────
const isOpen = ref(false)
const options = shallowRef<ConfirmOptions>({ title: '', message: '' })
let resolveFn: ((value: boolean) => void) | null = null

export function useConfirm() {
  /**
   * Show the confirmation dialog and return a Promise that resolves
   * to true (user confirmed) or false (user dismissed).
   */
  function confirm(opts: ConfirmOptions): Promise<boolean> {
    options.value = opts
    isOpen.value = true
    return new Promise<boolean>((resolve) => {
      resolveFn = resolve
    })
  }

  function handleConfirm() {
    isOpen.value = false
    resolveFn?.(true)
    resolveFn = null
  }

  function handleCancel() {
    isOpen.value = false
    resolveFn?.(false)
    resolveFn = null
  }

  return { isOpen, options, confirm, handleConfirm, handleCancel }
}
