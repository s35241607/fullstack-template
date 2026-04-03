<script setup lang="ts">
  import { useProcurementPlans } from '@/composables/useProcurementPlans'
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    Plus,
    Trash2,
    RefreshCw,
    AlertCircle,
    PackageOpen,
    Loader2,
    Send,
    Eye,
  } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'

  const router = useRouter()
  const { plans, isLoading, error, createPlan, deletePlan, submitPlan, refresh } =
    useProcurementPlans()

  const newName = ref('')
  const newDate = ref('')
  const isCreating = ref(false)
  const deletingId = ref<string | null>(null)
  const submittingId = ref<string | null>(null)

  function handleRefresh() {
    void refresh()
    toast.info('正在重新整理…')
  }

  async function handleCreate() {
    if (!newName.value.trim() || !newDate.value) return
    isCreating.value = true
    try {
      await createPlan(newName.value.trim(), newDate.value)
      toast.success('已建立採購計畫', { description: `「${newName.value.trim()}」已新增。` })
      newName.value = ''
      newDate.value = ''
    } catch (err) {
      toast.error('建立失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isCreating.value = false
    }
  }

  async function handleDelete(id: string, name: string) {
    deletingId.value = id
    try {
      await deletePlan(id)
      toast.success('已刪除', { description: `「${name}」已移除。` })
    } catch (err) {
      toast.error('刪除失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      deletingId.value = null
    }
  }

  async function handleSubmit(id: string, name: string) {
    submittingId.value = id
    try {
      await submitPlan(id)
      toast.success('已送審', { description: `「${name}」已送審。` })
    } catch (err) {
      toast.error('送審失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      submittingId.value = null
    }
  }

  function formatCurrency(n: number) {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      maximumFractionDigits: 0,
    }).format(n)
  }

  const statusMap: Record<string, { label: string; class: string }> = {
    DRAFT: {
      label: '草稿',
      class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    },
    SUBMITTED: {
      label: '已送審',
      class: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    },
    EE_REVIEW: {
      label: 'EE 審查中',
      class: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    },
    QUOTED: {
      label: '已報價',
      class: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400',
    },
    APPROVED: {
      label: '已核准',
      class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    },
    BUDGET_SUBMITTED: {
      label: '已送預算',
      class: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
    },
  }

  function getStatus(s: string) {
    return statusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }
</script>

<template>
  <div class="space-y-6 max-w-4xl">
    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">採購計畫</h1>
        <p class="text-sm text-muted-foreground mt-1">管理採購規劃，新增設備項目後送審。</p>
      </div>
      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors shrink-0"
        :disabled="isLoading"
        @click="handleRefresh"
      >
        <RefreshCw :size="14" :class="isLoading ? 'animate-spin' : ''" />
        <span class="hidden sm:inline">重新整理</span>
      </button>
    </div>

    <!-- Create form -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30">
        <h2 class="text-sm font-medium text-foreground">新增採購計畫</h2>
      </div>
      <div class="p-4 flex flex-col sm:flex-row gap-2">
        <input
          v-model="newName"
          type="text"
          placeholder="計畫名稱 *"
          class="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
          @keydown.enter="handleCreate"
        />
        <input
          v-model="newDate"
          type="date"
          class="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
        />
        <button
          :disabled="!newName.trim() || !newDate || isCreating"
          class="flex items-center justify-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity shrink-0"
          @click="handleCreate"
        >
          <Loader2 v-if="isCreating" :size="14" class="animate-spin" />
          <Plus v-else :size="14" />
          新增
        </button>
      </div>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
    >
      <AlertCircle :size="16" class="shrink-0" />
      <span>{{ error instanceof Error ? error.message : String(error) }}</span>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
        <h2 class="text-sm font-medium text-foreground">採購計畫清單</h2>
        <span class="text-xs text-muted-foreground">{{ plans.length }} 筆</span>
      </div>

      <!-- Loading -->
      <div
        v-if="isLoading && plans.length === 0"
        class="flex items-center justify-center py-12 text-muted-foreground"
      >
        <Loader2 :size="20" class="animate-spin mr-2" /> 載入中…
      </div>

      <!-- Empty -->
      <div
        v-else-if="plans.length === 0"
        class="flex flex-col items-center py-12 text-muted-foreground"
      >
        <PackageOpen :size="36" class="mb-2 opacity-40" />
        <p class="text-sm">尚未建立採購計畫</p>
      </div>

      <!-- List -->
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-border text-left text-muted-foreground bg-muted/40">
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">名稱</th>
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">預計採購日</th>
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">狀態</th>
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
              總金額
            </th>
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
              項目數
            </th>
            <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
              操作
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="plan in plans"
            :key="plan.id"
            class="border-b border-border/50 last:border-b-0 hover:bg-muted/30 transition-colors"
          >
            <td class="px-5 py-3 font-medium text-foreground">{{ plan.name }}</td>
            <td class="px-5 py-3 text-muted-foreground">{{ plan.planned_date }}</td>
            <td class="px-5 py-3">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="getStatus(plan.status).class"
              >
                {{ getStatus(plan.status).label }}
              </span>
            </td>
            <td class="px-5 py-3 text-right text-muted-foreground">
              {{ formatCurrency(plan.total_amount) }}
            </td>
            <td class="px-5 py-3 text-right text-muted-foreground">{{ plan.items.length }}</td>
            <td class="px-5 py-3 text-right">
              <div class="flex items-center justify-end gap-1">
                <button
                  class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  title="檢視詳情"
                  @click="router.push({ name: 'procurement-plan-detail', params: { id: plan.id } })"
                >
                  <Eye :size="14" />
                </button>
                <button
                  v-if="plan.status === 'DRAFT'"
                  class="p-1.5 rounded-md text-blue-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                  title="送審"
                  :disabled="submittingId === plan.id || plan.items.length === 0"
                  @click="handleSubmit(plan.id, plan.name)"
                >
                  <Loader2 v-if="submittingId === plan.id" :size="14" class="animate-spin" />
                  <Send v-else :size="14" />
                </button>
                <button
                  v-if="plan.status === 'DRAFT'"
                  class="p-1.5 rounded-md text-destructive hover:bg-destructive/10 transition-colors"
                  title="刪除"
                  :disabled="deletingId === plan.id"
                  @click="handleDelete(plan.id, plan.name)"
                >
                  <Loader2 v-if="deletingId === plan.id" :size="14" class="animate-spin" />
                  <Trash2 v-else :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
