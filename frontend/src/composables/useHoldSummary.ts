import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { ordersApi, type ModelHoldSummary, type ModelHoldDetail } from '@/services/api'

export function useHoldSummary() {
  const summaries = ref<ModelHoldSummary[]>([])

  const {
    isLoading,
    error,
    execute: refresh,
  } = useAsyncState(
    async () => {
      summaries.value = await ordersApi.holdSummary()
    },
    undefined,
    { immediate: true },
  )

  const holdDetails = ref<ModelHoldDetail[]>([])
  const isLoadingDetails = ref(false)

  async function loadModelDetails(modelName: string) {
    isLoadingDetails.value = true
    try {
      holdDetails.value = await ordersApi.holdsByModel(modelName)
    } finally {
      isLoadingDetails.value = false
    }
  }

  return {
    summaries: readonly(summaries),
    holdDetails: readonly(holdDetails),
    isLoading,
    isLoadingDetails,
    error,
    refresh,
    loadModelDetails,
  }
}
