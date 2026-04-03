import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { notificationsApi, type Notification } from '@/services/api'

export function useNotifications() {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)

  const {
    isLoading,
    error,
    execute: refresh,
  } = useAsyncState(
    async () => {
      const [list, count] = await Promise.all([
        notificationsApi.list(),
        notificationsApi.unreadCount(),
      ])
      notifications.value = list
      unreadCount.value = count.count
    },
    undefined,
    { immediate: true },
  )

  async function markRead(id: string) {
    const updated = await notificationsApi.markRead(id)
    const idx = notifications.value.findIndex((n) => n.id === id)
    if (idx !== -1) notifications.value[idx] = updated
    unreadCount.value = notifications.value.filter((n) => !n.is_read).length
  }

  async function markAllRead() {
    await notificationsApi.markAllRead()
    notifications.value = notifications.value.map((n) => ({ ...n, is_read: true }))
    unreadCount.value = 0
  }

  return {
    notifications: readonly(notifications),
    unreadCount: readonly(unreadCount),
    isLoading,
    error,
    refresh,
    markRead,
    markAllRead,
  }
}
