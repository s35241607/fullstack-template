<script setup lang="ts">
  import { Bell, CheckCheck, Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-vue-next'
  import { useNotifications } from '@/composables/useNotifications'
  import {
    Popover,
    PopoverContent,
    PopoverTrigger,
  } from '@/components/ui/popover'
  import { Button } from '@/components/ui/button'

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
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="ghost" size="icon-sm" class="relative" aria-label="Notifications">
        <Bell class="h-4 w-4" />
        <span
          v-if="unreadCount > 0"
          class="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[16px] h-4 px-1 text-[10px] font-semibold leading-none bg-destructive text-destructive-foreground rounded-full"
        >
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </span>
      </Button>
    </PopoverTrigger>

    <PopoverContent
      side="bottom"
      align="end"
      :side-offset="8"
      class="w-80 p-0 overflow-hidden"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 class="text-sm font-semibold text-foreground">{{ $t('header.notificationsTitle') }}</h3>
        <button
          v-if="unreadCount > 0"
          class="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          @click="markAllRead"
        >
          <CheckCheck :size="14" />
          {{ $t('header.markAllRead') }}
        </button>
      </div>

      <!-- Body -->
      <div class="overflow-y-auto max-h-[340px]">
        <!-- Loading -->
        <div v-if="isLoading" class="flex items-center justify-center py-8 text-sm text-muted-foreground">
          {{ $t('common.loading') }}
        </div>

        <!-- Empty -->
        <div v-else-if="notifications.length === 0" class="flex flex-col items-center justify-center py-8 text-muted-foreground">
          <Bell :size="28" class="mb-2 opacity-40" />
          <span class="text-sm">{{ $t('header.noNotifications') }}</span>
        </div>

        <!-- List -->
        <template v-else>
          <button
            v-for="n in notifications"
            :key="n.id"
            class="flex items-start gap-3 w-full px-4 py-3 text-left hover:bg-accent/50 transition-colors border-b border-border/50 last:border-b-0 cursor-pointer"
            :class="{ 'bg-accent/20': !n.is_read }"
            @click="!n.is_read && markRead(n.id)"
          >
            <component :is="typeIcon[n.type]" :size="16" class="mt-0.5 shrink-0" :class="typeColor[n.type]" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium leading-tight" :class="{ 'text-foreground': !n.is_read, 'text-muted-foreground': n.is_read }">
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
  </Popover>
</template>
