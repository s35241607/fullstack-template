import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error.response?.data ?? error.message)
    return Promise.reject(error)
  },
)

// ── Notification Types ─────────────────────────────────────────────────────────

export interface Notification {
  id: string
  title: string
  message: string
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'
  is_read: boolean
  link: string | null
  created_at: string
}

export interface UnreadCount {
  count: number
}

// ── Notification API ───────────────────────────────────────────────────────────

export const notificationsApi = {
  list: (unreadOnly = false) =>
    apiClient
      .get<Notification[]>('/notifications/', { params: { unread_only: unreadOnly } })
      .then((r) => r.data),

  unreadCount: () => apiClient.get<UnreadCount>('/notifications/unread-count').then((r) => r.data),

  markRead: (id: string) =>
    apiClient.patch<Notification>(`/notifications/${id}/read`).then((r) => r.data),

  markAllRead: () => apiClient.post('/notifications/read-all'),
}
