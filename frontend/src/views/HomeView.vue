<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { ClipboardList, PauseCircle, ShoppingCart, FileText, Zap } from 'lucide-vue-next'
  import { useI18n } from 'vue-i18n'
  import { ordersApi, procurementApi } from '@/services/api'

  const { t } = useI18n()

  const orderCount = ref(0)
  const holdCount = ref(0)
  const planCount = ref(0)
  const loading = ref(true)
  const apiDocsUrl = import.meta.env.VITE_API_DOCS_URL || '/docs'

  onMounted(async () => {
    try {
      const [orders, holds, plans] = await Promise.all([
        ordersApi.list().catch(() => []),
        ordersApi.holdSummary().catch(() => []),
        procurementApi.listPlans().catch(() => []),
      ])
      orderCount.value = orders.length
      holdCount.value = (holds as Array<{ total_hold_quantity: number }>).reduce(
        (sum, m) => sum + m.total_hold_quantity,
        0,
      )
      planCount.value = plans.length
    } finally {
      loading.value = false
    }
  })

  const modules = [
    {
      key: 'orders',
      icon: ClipboardList,
      path: '/orders',
      accent: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    },
    {
      key: 'holds',
      icon: PauseCircle,
      path: '/orders/holds',
      accent: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    },
    {
      key: 'procurement',
      icon: ShoppingCart,
      path: '/procurement',
      accent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    },
    {
      key: 'api',
      icon: Zap,
      path: apiDocsUrl,
      external: true,
      accent: 'bg-teal-500/10 text-teal-600 dark:text-teal-400',
    },
  ]
</script>

<template>
  <div class="space-y-8 max-w-5xl">
    <!-- Hero -->
    <div class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div
          class="flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground text-xl font-bold shrink-0"
        >
          <FileText :size="24" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-foreground tracking-tight">{{ $t('home.title') }}</h1>
          <p class="text-muted-foreground mt-1">{{ $t('home.subtitle') }}</p>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">{{ $t('home.stats.orders') }}</p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ orderCount }}</span>
        </p>
      </div>
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {{ $t('home.stats.holds') }}
        </p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ holdCount.toLocaleString() }}</span>
        </p>
      </div>
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">{{ $t('home.stats.plans') }}</p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ planCount }}</span>
        </p>
      </div>
    </div>

    <!-- Module cards -->
    <div>
      <h2 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
        {{ $t('home.modules') }}
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <component
          :is="m.external ? 'a' : 'RouterLink'"
          v-for="m in modules"
          :key="m.key"
          v-bind="m.external ? { href: m.path, target: '_blank', rel: 'noopener' } : { to: m.path }"
          class="group flex flex-col gap-3 rounded-lg border border-border bg-card p-4 hover:border-primary/30 hover:shadow-sm transition-[border-color,box-shadow]"
        >
          <div
            class="flex items-center justify-center w-9 h-9 rounded-md transition-colors"
            :class="m.accent"
          >
            <component :is="m.icon" :size="18" />
          </div>
          <div>
            <p
              class="font-medium text-foreground text-sm group-hover:text-primary transition-colors"
            >
              {{ $t(`home.moduleCards.${m.key}.title`) }}
            </p>
            <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
              {{ $t(`home.moduleCards.${m.key}.desc`) }}
            </p>
          </div>
        </component>
      </div>
    </div>
  </div>
</template>
