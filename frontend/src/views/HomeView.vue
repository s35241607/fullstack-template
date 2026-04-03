<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { ClipboardList, PauseCircle, ShoppingCart, FileText, Zap } from 'lucide-vue-next'
  import { ordersApi, procurementApi } from '@/services/api'

  const orderCount = ref(0)
  const holdCount = ref(0)
  const planCount = ref(0)
  const loading = ref(true)

  onMounted(async () => {
    try {
      const [orders, holds, plans] = await Promise.all([
        ordersApi.list().catch(() => ({ data: [] })),
        ordersApi.holdSummary().catch(() => ({ data: [] })),
        procurementApi.list().catch(() => ({ data: [] })),
      ])
      orderCount.value = orders.data.length
      holdCount.value = (holds.data as Array<{ total_hold_quantity: number }>).reduce(
        (sum, m) => sum + m.total_hold_quantity,
        0,
      )
      planCount.value = plans.data.length
    } finally {
      loading.value = false
    }
  })

  const modules = [
    {
      title: '訂單管理',
      desc: '查看所有採購訂單、品項明細、收貨紀錄與交期追蹤',
      icon: ClipboardList,
      path: '/orders',
      accent: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    },
    {
      title: 'On-Hold 總覽',
      desc: '依機型彙總 Hold 數量，快速掌握暫扣狀況',
      icon: PauseCircle,
      path: '/orders/holds',
      accent: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    },
    {
      title: '採購計畫',
      desc: '建立與管理採購計畫，支援完整審核流程',
      icon: ShoppingCart,
      path: '/procurement',
      accent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    },
    {
      title: 'API 文件',
      desc: 'FastAPI 自動生成的 OpenAPI 文件',
      icon: Zap,
      path: 'http://localhost:8000/docs',
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
          <h1 class="text-2xl font-bold text-foreground tracking-tight">企業採購管理系統</h1>
          <p class="text-muted-foreground mt-1">訂單追蹤 · On-Hold 管理 · 採購計畫審核</p>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">進行中訂單</p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ orderCount }}</span>
        </p>
      </div>
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Hold 暫扣總量
        </p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ holdCount.toLocaleString() }}</span>
        </p>
      </div>
      <div class="rounded-lg border border-border bg-card p-5">
        <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">採購計畫</p>
        <p class="text-3xl font-bold text-foreground mt-2">
          <span v-if="loading" class="text-muted-foreground">—</span>
          <span v-else>{{ planCount }}</span>
        </p>
      </div>
    </div>

    <!-- Module cards -->
    <div>
      <h2 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
        功能模組
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <component
          :is="m.external ? 'a' : 'RouterLink'"
          v-for="m in modules"
          :key="m.title"
          v-bind="m.external ? { href: m.path, target: '_blank', rel: 'noopener' } : { to: m.path }"
          class="group flex flex-col gap-3 rounded-lg border border-border bg-card p-4 hover:border-primary/30 hover:shadow-sm transition-all"
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
              {{ m.title }}
            </p>
            <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
              {{ m.desc }}
            </p>
          </div>
        </component>
      </div>
    </div>
  </div>
</template>
