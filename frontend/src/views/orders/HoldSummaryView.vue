<script setup lang="ts">
  import { useHoldSummary } from '@/composables/useHoldSummary'
  import { ref } from 'vue'
  import {
    RefreshCw,
    AlertCircle,
    Loader2,
    PauseCircle,
    ChevronDown,
    ChevronUp,
    PackageOpen,
  } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'

  const { summaries, holdDetails, isLoading, isLoadingDetails, error, refresh, loadModelDetails } =
    useHoldSummary()

  const expandedModel = ref<string | null>(null)

  function handleRefresh() {
    void refresh()
    toast.info('正在重新整理…')
  }

  async function toggleModel(modelName: string) {
    if (expandedModel.value === modelName) {
      expandedModel.value = null
      return
    }
    expandedModel.value = modelName
    await loadModelDetails(modelName)
  }
</script>

<template>
  <div class="space-y-6 max-w-5xl">
    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">On-Hold 總覽</h1>
        <p class="text-sm text-muted-foreground mt-1">
          依機型查看所有 On-Hold 數量與相關訂單明細。
        </p>
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

    <!-- Error -->
    <div
      v-if="error"
      class="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
    >
      <AlertCircle :size="16" class="shrink-0" />
      <span>{{ error instanceof Error ? error.message : String(error) }}</span>
    </div>

    <!-- Loading -->
    <div
      v-if="isLoading && summaries.length === 0"
      class="flex items-center justify-center py-12 text-muted-foreground"
    >
      <Loader2 :size="20" class="animate-spin mr-2" /> 載入中…
    </div>

    <!-- Empty -->
    <div
      v-else-if="summaries.length === 0"
      class="rounded-xl border border-border bg-card p-12 flex flex-col items-center text-muted-foreground"
    >
      <PackageOpen :size="36" class="mb-2 opacity-40" />
      <p class="text-sm">目前沒有 On-Hold 紀錄</p>
    </div>

    <!-- Summary cards -->
    <div v-else class="space-y-3">
      <!-- Stats overview -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">涉及機型</p>
          <p class="text-2xl font-bold text-foreground">{{ summaries.length }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">Hold 筆數合計</p>
          <p class="text-2xl font-bold text-amber-600">
            {{ summaries.reduce((s, m) => s + m.hold_count, 0) }}
          </p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">Hold 數量合計</p>
          <p class="text-2xl font-bold text-amber-600">
            {{ summaries.reduce((s, m) => s + m.total_hold_quantity, 0) }}
          </p>
        </div>
      </div>

      <!-- Model list -->
      <div class="rounded-xl border border-border bg-card overflow-hidden">
        <div class="px-5 py-3 border-b border-border bg-muted/30">
          <h2 class="text-sm font-medium text-foreground">依機型分類</h2>
        </div>
        <div class="divide-y divide-border">
          <div v-for="summary in summaries" :key="summary.model_name">
            <!-- Model row -->
            <button
              class="w-full flex items-center gap-4 px-5 py-3.5 hover:bg-muted/30 transition-colors text-left"
              @click="toggleModel(summary.model_name)"
            >
              <div
                class="flex items-center justify-center w-9 h-9 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 shrink-0"
              >
                <PauseCircle :size="18" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-foreground">{{ summary.model_name }}</p>
                <p class="text-xs text-muted-foreground mt-0.5">
                  {{ summary.hold_count }} 筆 Hold，共 {{ summary.total_hold_quantity }} 個
                </p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-sm font-semibold bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                >
                  {{ summary.total_hold_quantity }}
                </span>
                <ChevronUp
                  v-if="expandedModel === summary.model_name"
                  :size="16"
                  class="text-muted-foreground"
                />
                <ChevronDown v-else :size="16" class="text-muted-foreground" />
              </div>
            </button>

            <!-- Expanded details -->
            <div v-if="expandedModel === summary.model_name" class="px-5 pb-4 bg-muted/10">
              <div
                v-if="isLoadingDetails"
                class="flex items-center justify-center py-4 text-muted-foreground"
              >
                <Loader2 :size="16" class="animate-spin mr-2" /> 載入明細…
              </div>
              <table v-else-if="holdDetails.length > 0" class="w-full text-xs mt-2">
                <thead>
                  <tr class="text-left text-muted-foreground border-b border-border">
                    <th class="pb-2 font-medium">訂單編號</th>
                    <th class="pb-2 font-medium">供應商</th>
                    <th class="pb-2 font-medium">物料名稱</th>
                    <th class="pb-2 font-medium text-right">訂購量</th>
                    <th class="pb-2 font-medium text-right">Hold 數量</th>
                    <th class="pb-2 font-medium">原因</th>
                    <th class="pb-2 font-medium">Hold 人</th>
                    <th class="pb-2 font-medium">日期</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="detail in holdDetails"
                    :key="detail.hold_id"
                    class="border-b border-border/50 last:border-b-0"
                  >
                    <td class="py-2 font-medium text-foreground">{{ detail.order_number }}</td>
                    <td class="py-2 text-muted-foreground">{{ detail.supplier_name }}</td>
                    <td class="py-2 text-muted-foreground">{{ detail.material_name }}</td>
                    <td class="py-2 text-right text-muted-foreground">
                      {{ detail.ordered_quantity }}
                    </td>
                    <td class="py-2 text-right font-semibold text-amber-600">
                      {{ detail.hold_quantity }}
                    </td>
                    <td class="py-2 text-muted-foreground">{{ detail.reason }}</td>
                    <td class="py-2 text-muted-foreground">{{ detail.held_by }}</td>
                    <td class="py-2 text-muted-foreground">
                      {{ detail.created_at?.slice(0, 10) }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-xs text-muted-foreground py-4">無明細資料</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
