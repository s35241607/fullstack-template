import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { ordersApi, type PurchaseOrder } from '@/services/api'

export function useOrders() {
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

  async function createOrder(data: {
    order_number: string
    supplier_name: string
    supplier_code?: string
    order_date: string
    expected_delivery_date: string
    notes?: string
  }) {
    const order = await ordersApi.create(data)
    orders.value.push(order)
    return order
  }

  async function deleteOrder(id: string) {
    await ordersApi.delete(id)
    orders.value = orders.value.filter((o) => o.id !== id)
  }

  async function cancelOrder(id: string) {
    const updated = await ordersApi.cancel(id)
    const idx = orders.value.findIndex((o) => o.id === id)
    if (idx !== -1) orders.value[idx] = updated
    return updated
  }

  return {
    orders: readonly(orders),
    isLoading,
    error,
    refresh,
    createOrder,
    deleteOrder,
    cancelOrder,
  }
}
