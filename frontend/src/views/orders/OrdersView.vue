<script setup lang="ts">
  import { useOrders } from '@/composables/useOrders'
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    Plus,
    Trash2,
    RefreshCw,
    AlertCircle,
    PackageOpen,
    Loader2,
    Eye,
    Ban,
  } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'
  import DatePicker from '@/components/ui/date-picker/DatePicker.vue'
  import { useConfirm } from '@/composables/useConfirm'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'

  const router = useRouter()
  const { orders, isLoading, error, createOrder, deleteOrder, cancelOrder, refresh } = useOrders()
  const { confirm } = useConfirm()

  // Create form
  const showCreateForm = ref(false)
  const newOrderNumber = ref('')
  const newSupplierName = ref('')
  const newSupplierCode = ref('')
  const newOrderDate = ref('')
  const newExpectedDate = ref('')
  const newNotes = ref('')
  const isCreating = ref(false)
  const deletingId = ref<string | null>(null)
  const cancellingId = ref<string | null>(null)

  function handleRefresh() {
    void refresh()
    toast.info('正在重新整理…')
  }

  async function handleCreate() {
    if (
      !newOrderNumber.value.trim() ||
      !newSupplierName.value.trim() ||
      !newOrderDate.value ||
      !newExpectedDate.value
    )
      return
    isCreating.value = true
    try {
      await createOrder({
        order_number: newOrderNumber.value.trim(),
        supplier_name: newSupplierName.value.trim(),
        supplier_code: newSupplierCode.value.trim(),
        order_date: newOrderDate.value,
        expected_delivery_date: newExpectedDate.value,
        notes: newNotes.value.trim(),
      })
      toast.success('已建立訂單', { description: `訂單「${newOrderNumber.value.trim()}」已新增。` })
      newOrderNumber.value = ''
      newSupplierName.value = ''
      newSupplierCode.value = ''
      newOrderDate.value = ''
      newExpectedDate.value = ''
      newNotes.value = ''
      showCreateForm.value = false
    } catch (err) {
      toast.error('建立失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isCreating.value = false
    }
  }

  async function handleDelete(id: string, name: string) {
    const confirmed = await confirm({
      title: '確認刪除訂單',
      message: `確定要刪除訂單「${name}」嗎？此操作無法復原。`,
      confirmText: '刪除',
      cancelText: '取消',
      variant: 'destructive',
    })
    if (!confirmed) return
    deletingId.value = id
    try {
      await deleteOrder(id)
      toast.success('已刪除', { description: `訂單「${name}」已移除。` })
    } catch (err) {
      toast.error('刪除失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      deletingId.value = null
    }
  }

  async function handleCancel(id: string, name: string) {
    const confirmed = await confirm({
      title: '確認取消訂單',
      message: `確定要取消訂單「${name}」嗎？取消後無法恢復為進行中狀態。`,
      confirmText: '取消訂單',
      cancelText: '返回',
      variant: 'destructive',
    })
    if (!confirmed) return
    cancellingId.value = id
    try {
      await cancelOrder(id)
      toast.success('已取消', { description: `訂單「${name}」已取消。` })
    } catch (err) {
      toast.error('取消失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      cancellingId.value = null
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
    OPEN: {
      label: '進行中',
      class: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    },
    PARTIALLY_RECEIVED: {
      label: '部分到貨',
      class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
    },
    FULLY_RECEIVED: {
      label: '全部到貨',
      class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    },
    CLOSED: {
      label: '已結案',
      class: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
    },
    CANCELLED: {
      label: '已取消',
      class: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    },
  }

  function getStatus(s: string) {
    return statusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }
</script>

<template>
  <div class="space-y-6 max-w-5xl">
    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">訂單管理</h1>
        <p class="text-sm text-muted-foreground mt-1">管理採購訂單，追蹤到貨及 On-Hold 狀態。</p>
      </div>
      <div class="flex gap-2">
        <button
          class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors shrink-0"
          :disabled="isLoading"
          @click="handleRefresh"
        >
          <RefreshCw :size="14" :class="isLoading ? 'animate-spin' : ''" />
          <span class="hidden sm:inline">重新整理</span>
        </button>
        <button
          class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm bg-primary text-primary-foreground hover:opacity-90 transition-opacity shrink-0"
          @click="showCreateForm = !showCreateForm"
        >
          <Plus :size="14" />
          新增訂單
        </button>
      </div>
    </div>

    <!-- Create form -->
    <div v-if="showCreateForm" class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30">
        <h2 class="text-sm font-medium text-foreground">新增採購訂單</h2>
      </div>
      <div class="p-4 space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <Label for="new-order-number">訂單編號 <span class="text-destructive">*</span></Label>
            <Input
              id="new-order-number"
              v-model="newOrderNumber"
              name="order_number"
              autocomplete="off"
              placeholder="例如 PO-2026-0001"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="new-order-supplier-name">供應商名稱 <span class="text-destructive">*</span></Label>
            <Input
              id="new-order-supplier-name"
              v-model="newSupplierName"
              name="supplier_name"
              autocomplete="organization"
              placeholder="供應商名稱"
            />
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="space-y-1.5">
            <Label for="new-order-supplier-code">供應商代碼</Label>
            <Input
              id="new-order-supplier-code"
              v-model="newSupplierCode"
              name="supplier_code"
              autocomplete="off"
              placeholder="選填"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="new-order-date">訂單日期 <span class="text-destructive">*</span></Label>
            <DatePicker id="new-order-date" v-model="newOrderDate" placeholder="訂單日期" />
          </div>
          <div class="space-y-1.5">
            <Label for="new-order-expected-date">預期交貨日 <span class="text-destructive">*</span></Label>
            <DatePicker id="new-order-expected-date" v-model="newExpectedDate" placeholder="預期交貨日" />
          </div>
        </div>
        <div class="space-y-1.5">
          <Label for="new-order-notes">備註</Label>
          <Input
            id="new-order-notes"
            v-model="newNotes"
            name="notes"
            autocomplete="off"
            placeholder="選填"
          />
        </div>
        <div class="flex justify-end gap-2">
          <button
            class="px-4 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
            @click="showCreateForm = false"
          >
            取消
          </button>
          <button
            :disabled="
              !newOrderNumber.trim() ||
                !newSupplierName.trim() ||
                !newOrderDate ||
                !newExpectedDate ||
                isCreating
            "
            class="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            @click="handleCreate"
          >
            <Loader2 v-if="isCreating" :size="14" class="animate-spin" />
            <Plus v-else :size="14" />
            建立
          </button>
        </div>
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
        <h2 class="text-sm font-medium text-foreground">訂單清單</h2>
        <span class="text-xs text-muted-foreground">{{ orders.length }} 筆</span>
      </div>

      <!-- Loading -->
      <div
        v-if="isLoading && orders.length === 0"
        class="flex items-center justify-center py-12 text-muted-foreground"
      >
        <Loader2 :size="20" class="animate-spin mr-2" /> 載入中…
      </div>

      <!-- Empty -->
      <div
        v-else-if="orders.length === 0"
        class="flex flex-col items-center py-12 text-muted-foreground"
      >
        <PackageOpen :size="36" class="mb-2 opacity-40" />
        <p class="text-sm">尚未建立訂單</p>
      </div>

      <!-- List -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-border text-left text-muted-foreground bg-muted/40">
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">訂單編號</th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">供應商</th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">訂單日期</th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">預期交貨</th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider">狀態</th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
                金額
              </th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
                到貨
              </th>
              <th class="px-5 py-2.5 font-medium text-xs uppercase tracking-wider text-right">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="order in orders"
              :key="order.id"
              class="border-b border-border/50 last:border-b-0 hover:bg-muted/30 transition-colors"
            >
              <td class="px-5 py-3 font-medium text-foreground">{{ order.order_number }}</td>
              <td class="px-5 py-3 text-muted-foreground">{{ order.supplier_name }}</td>
              <td class="px-5 py-3 text-muted-foreground">{{ order.order_date }}</td>
              <td class="px-5 py-3 text-muted-foreground">{{ order.expected_delivery_date }}</td>
              <td class="px-5 py-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatus(order.status).class"
                >
                  {{ getStatus(order.status).label }}
                </span>
              </td>
              <td class="px-5 py-3 text-right text-muted-foreground">
                {{ formatCurrency(order.total_amount) }}
              </td>
              <td class="px-5 py-3 text-right text-muted-foreground">
                {{ order.total_received }} / {{ order.total_ordered }}
              </td>
              <td class="px-5 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    :aria-label="`檢視 ${order.order_number} 詳情`"
                    title="檢視詳情"
                    @click="router.push({ name: 'order-detail', params: { id: order.id } })"
                  >
                    <Eye :size="14" />
                  </button>
                  <button
                    v-if="order.status === 'OPEN'"
                    class="p-1.5 rounded-md text-amber-500 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-colors"
                    :aria-label="`取消 ${order.order_number}`"
                    title="取消訂單"
                    :disabled="cancellingId === order.id"
                    @click="handleCancel(order.id, order.order_number)"
                  >
                    <Loader2 v-if="cancellingId === order.id" :size="14" class="animate-spin" />
                    <Ban v-else :size="14" />
                  </button>
                  <button
                    v-if="order.status === 'OPEN' && order.items.length === 0"
                    class="p-1.5 rounded-md text-destructive hover:bg-destructive/10 transition-colors"
                    :aria-label="`刪除 ${order.order_number}`"
                    title="刪除"
                    :disabled="deletingId === order.id"
                    @click="handleDelete(order.id, order.order_number)"
                  >
                    <Loader2 v-if="deletingId === order.id" :size="14" class="animate-spin" />
                    <Trash2 v-else :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
