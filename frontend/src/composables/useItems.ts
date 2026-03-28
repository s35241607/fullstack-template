import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { itemsApi, type Item } from '@/services/api'

export function useItems() {
  const items = ref<Item[]>([])

  const { isLoading, error, execute: refresh } = useAsyncState(
    async () => {
      items.value = await itemsApi.list()
    },
    undefined,
    { immediate: true },
  )

  async function createItem(name: string, description = '') {
    const item = await itemsApi.create({ name, description })
    items.value.push(item)
    return item
  }

  async function deleteItem(id: string) {
    await itemsApi.delete(id)
    items.value = items.value.filter((i) => i.id !== id)
  }

  return {
    items: readonly(items),
    isLoading,
    error,
    refresh,
    createItem,
    deleteItem,
  }
}
