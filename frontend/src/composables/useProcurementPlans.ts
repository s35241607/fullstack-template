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

  async function submitPlan(id: string) {
    const updated = await procurementApi.submitPlan(id)
    const idx = plans.value.findIndex((p) => p.id === id)
    if (idx !== -1) plans.value[idx] = updated
    return updated
  }

  return {
    plans: readonly(plans),
    isLoading,
    error,
    refresh,
    createPlan,
    deletePlan,
    submitPlan,
  }
}
