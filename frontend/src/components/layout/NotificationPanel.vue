<script setup lang="ts">
  import { PopoverRoot, PopoverTrigger, PopoverContent, PopoverPortal } from 'radix-vue'
  import { Bell, CheckCheck, Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-vue-next'
  import { useNotifications } from '@/composables/useNotifications'

  const { notifications, unreadCount, isLoading, markRead, markAllRead } = useNotifications()

  const typeIcon = {
    INFO: Info,
    SUCCESS: CheckCircle,
    WARNING: AlertTriangle,
    ERROR: XCircle,
  } as const

  const typeColor = {
    INFO: 'text-blue-500',
    SUCCESS: 'text-green-500',
    WARNING: 'text-yellow-500',
    ERROR: 'text-red-500',
  } as const

  function formatTime(dateStr: string) {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return '剛剛'
    if (mins < 60) return `${mins} 分鐘前`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} 小時前`
    const days = Math.floor(hours / 24)
    return `${days} 天前`
  }
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <button
        class="relative p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        aria-label="Notifications"
      >
        <Bell :size="18" />
        <span
          v-if="unreadCount > 0"
          class="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[16px] h-4 px-1 text-[10px] font-semibold leading-none bg-destructive text-destructive-foreground rounded-full"
        >
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </span>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        side="bottom"
        align="end"
        :side-offset="8"
        class="z-50 w-80 max-h-[420px] bg-popover text-popover-foreground border border-border rounded-lg shadow-lg outline-none animate-in fade-in-0 zoom-in-95 data-[side=bottom]:slide-in-from-top-2"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-border">
          <h3 class="text-sm font-semibold">通知</h3>
          <button
            v-if="unreadCount > 0"
            class="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            @click="markAllRead"
          >
            <CheckCheck :size="14" />
            全部已讀
          </button>
        </div>

        <!-- Body -->
        <div class="overflow-y-auto max-h-[340px]">
          <!-- Loading -->
          <div
            v-if="isLoading"
            class="flex items-center justify-center py-8 text-sm text-muted-foreground"
          >
            載入中…
          </div>

          <!-- Empty -->
          <div
            v-else-if="notifications.length === 0"
            class="flex flex-col items-center justify-center py-8 text-muted-foreground"
          >
            <Bell :size="28" class="mb-2 opacity-40" />
            <span class="text-sm">目前沒有通知</span>
          </div>

          <!-- List -->
          <template v-else>
            <button
              v-for="n in notifications"
              :key="n.id"
              class="flex items-start gap-3 w-full px-4 py-3 text-left hover:bg-accent/50 transition-colors border-b border-border/50 last:border-b-0"
              :class="{ 'bg-accent/20': !n.is_read }"
              @click="!n.is_read && markRead(n.id)"
            >
              <component
                :is="typeIcon[n.type]"
                :size="16"
                class="mt-0.5 shrink-0"
                :class="typeColor[n.type]"
              />
              <div class="flex-1 min-w-0">
                <p
                  class="text-sm font-medium leading-tight"
                  :class="{ 'text-foreground': !n.is_read, 'text-muted-foreground': n.is_read }"
                >
                  {{ n.title }}
                </p>
                <p class="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                  {{ n.message }}
                </p>
                <span class="text-[11px] text-muted-foreground/70 mt-1 block">
                  {{ formatTime(n.created_at) }}
                </span>
              </div>
              <span v-if="!n.is_read" class="mt-1.5 w-2 h-2 rounded-full bg-primary shrink-0" />
            </button>
          </template>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
