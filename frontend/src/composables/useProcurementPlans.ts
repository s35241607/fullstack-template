import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { procurementApi, type ProcurementPlan } from '@/services/api'

export function useProcurementPlans() {
  const plans = ref<ProcurementPlan[]>([])

  const {
    isLoading,
    error,
    execute: refresh,
  } = useAsyncState(
    async () => {
      plans.value = await procurementApi.listPlans()
    },
    undefined,
    { immediate: true },
  )

  async function createPlan(name: string, planned_date: string) {
    const plan = await procurementApi.createPlan({ name, planned_date })
    plans.value.push(plan)
    return plan
  }

  async function deletePlan(id: string) {
    await procurementApi.deletePlan(id)
    plans.value = plans.value.filter((p) => p.id !== id)
  }

  function updateLocal(id: string, updated: ProcurementPlan) {
    const idx = plans.value.findIndex((p) => p.id === id)
    if (idx !== -1) plans.value[idx] = updated
    return updated
  }

  async function submitPlan(id: string) {
    return updateLocal(id, await procurementApi.submitPlan(id))
  }

  async function sendToEeReview(id: string) {
    return updateLocal(id, await procurementApi.sendToEeReview(id))
  }

  async function markQuoted(id: string) {
    return updateLocal(id, await procurementApi.markQuoted(id))
  }

  async function approvePlan(id: string) {
    return updateLocal(id, await procurementApi.approvePlan(id))
  }

  async function submitToBudget(id: string) {
    return updateLocal(id, await procurementApi.submitToBudget(id))
  }

  return {
    plans: readonly(plans),
    isLoading,
    error,
    refresh,
    createPlan,
    deletePlan,
    submitPlan,
    sendToEeReview,
    markQuoted,
    approvePlan,
    submitToBudget,
  }
}
