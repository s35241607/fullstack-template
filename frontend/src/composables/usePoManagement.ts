import { ref } from 'vue'
import { useAsyncState } from '@vueuse/core'
import {
  ordersApi,
  type ApplyPullInPayload,
  type PurchaseOrder,
  type UpdatePurchaseOrderSchedulePayload,
} from '@/services/api'

export function usePoManagement() {
  const orders = ref<PurchaseOrder[]>([])

  const {
    isLoading,
    error,
    execute: refresh,
  } = useAsyncState(
    async () => {
      orders.value = await ordersApi.list()
    },
    undefined,
    { immediate: true },
  )

  function replaceOrder(updatedOrder: PurchaseOrder) {
    const index = orders.value.findIndex((order) => order.id === updatedOrder.id)
    if (index !== -1) {
      orders.value[index] = updatedOrder
    }

    return updatedOrder
  }

  async function applyPullIn(
    orderId: string,
    lineId: string,
    scheduleId: string,
    payload: ApplyPullInPayload,
  ) {
    return replaceOrder(await ordersApi.applyPullIn(orderId, lineId, scheduleId, payload))
  }

  async function updateSchedule(
    orderId: string,
    lineId: string,
    scheduleId: string,
    payload: UpdatePurchaseOrderSchedulePayload,
  ) {
    return replaceOrder(await ordersApi.updateSchedule(orderId, lineId, scheduleId, payload))
  }

  async function resetDemoData() {
    orders.value = await ordersApi.resetDemoData()
    return orders.value
  }

  return {
    orders: orders,
    isLoading,
    error,
    refresh,
    applyPullIn,
    updateSchedule,
    resetDemoData,
  }
}
