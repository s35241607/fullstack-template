<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ordersApi, type PurchaseOrder, type OrderItem } from '@/services/api'
  import {
    ArrowLeft,
    Plus,
    Trash2,
    Loader2,
    AlertCircle,
    PackageOpen,
    Ban,
    Lock,
    PackageCheck,
    PauseCircle,
    PlayCircle,
  } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'

  const route = useRoute()
  const router = useRouter()

  const order = ref<PurchaseOrder | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  // Add item form
  const showAddItem = ref(false)
  const newItemNumber = ref(1)
  const newMaterialName = ref('')
  const newModelName = ref('')
  const newSpec = ref('')
  const newQty = ref(1)
  const newUnitPrice = ref(0)
  const newDeliveryDate = ref('')
  const isAddingItem = ref(false)

  // Receiving form - per item
  const receivingItemId = ref<string | null>(null)
  const recQty = ref(1)
  const recDate = ref('')
  const recInspector = ref('')
  const recNote = ref('')
  const isAddingReceiving = ref(false)

  // Hold form - per item
  const holdItemId = ref<string | null>(null)
  const holdQty = ref(1)
  const holdReason = ref('')
  const holdBy = ref('')
  const isAddingHold = ref(false)
  const releasingHoldId = ref<string | null>(null)

  const isCancelling = ref(false)
  const isClosing = ref(false)

  const isOpen = computed(() => order.value?.status === 'OPEN')

  async function loadOrder() {
    isLoading.value = true
    error.value = null
    try {
      order.value = await ordersApi.get(route.params.id as string)
    } catch {
      error.value = '無法載入訂單'
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadOrder)

  async function handleAddItem() {
    if (!newMaterialName.value.trim() || !order.value) return
    isAddingItem.value = true
    try {
      const item = await ordersApi.addItem(order.value.id, {
        item_number: newItemNumber.value,
        material_name: newMaterialName.value.trim(),
        model_name: newModelName.value.trim(),
        specification: newSpec.value.trim(),
        quantity: newQty.value,
        unit_price: newUnitPrice.value,
        delivery_date: newDeliveryDate.value || undefined,
      })
      order.value.items.push(item)
      toast.success('已新增項目')
      newItemNumber.value = order.value.items.length + 1
      newMaterialName.value = ''
      newModelName.value = ''
      newSpec.value = ''
      newQty.value = 1
      newUnitPrice.value = 0
      newDeliveryDate.value = ''
      showAddItem.value = false
    } catch (err) {
      toast.error('新增失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isAddingItem.value = false
    }
  }

  async function handleAddReceiving(item: OrderItem) {
    if (!order.value || !recQty.value || !recDate.value) return
    isAddingReceiving.value = true
    try {
      const record = await ordersApi.addReceiving(order.value.id, item.id, {
        received_quantity: recQty.value,
        received_date: recDate.value,
        inspector: recInspector.value.trim(),
        note: recNote.value.trim(),
      })
      item.receiving_records.push(record)
      item.received_quantity += record.received_quantity
      toast.success('已登錄到貨')
      receivingItemId.value = null
      recQty.value = 1
      recDate.value = ''
      recInspector.value = ''
      recNote.value = ''
      await loadOrder()
    } catch (err) {
      toast.error('登錄失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isAddingReceiving.value = false
    }
  }

  async function handleAddHold(item: OrderItem) {
    if (!order.value || !holdQty.value || !holdReason.value.trim() || !holdBy.value.trim()) return
    isAddingHold.value = true
    try {
      const hold = await ordersApi.addHold(order.value.id, item.id, {
        hold_quantity: holdQty.value,
        reason: holdReason.value.trim(),
        held_by: holdBy.value.trim(),
      })
      item.holds.push(hold)
      toast.success('已設定 On-Hold')
      holdItemId.value = null
      holdQty.value = 1
      holdReason.value = ''
      holdBy.value = ''
      await loadOrder()
    } catch (err) {
      toast.error('設定失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isAddingHold.value = false
    }
  }

  async function handleReleaseHold(item: OrderItem, holdId: string) {
    if (!order.value) return
    releasingHoldId.value = holdId
    try {
      await ordersApi.releaseHold(order.value.id, item.id, holdId, 'current_user')
      toast.success('已釋放 Hold')
      await loadOrder()
    } catch (err) {
      toast.error('釋放失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      releasingHoldId.value = null
    }
  }

  async function handleCancel() {
    if (!order.value) return
    isCancelling.value = true
    try {
      order.value = await ordersApi.cancel(order.value.id)
      toast.success('訂單已取消')
    } catch (err) {
      toast.error('取消失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isCancelling.value = false
    }
  }

  async function handleClose() {
    if (!order.value) return
    isClosing.value = true
    try {
      order.value = await ordersApi.close(order.value.id)
      toast.success('訂單已結案')
    } catch (err) {
      toast.error('結案失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isClosing.value = false
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

  const itemStatusMap: Record<string, { label: string; class: string }> = {
    PENDING: {
      label: '待到貨',
      class: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    },
    PARTIALLY_RECEIVED: {
      label: '部分到貨',
      class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
    },
    FULLY_RECEIVED: {
      label: '已到齊',
      class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    },
  }

  function getStatus(s: string) {
    return statusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }

  function getItemStatus(s: string) {
    return itemStatusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }
</script>

<template>
  <div class="space-y-6 max-w-5xl">
    <!-- Back -->
    <button
      class="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      @click="router.push({ name: 'orders' })"
    >
      <ArrowLeft :size="14" />
      返回列表
    </button>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-20 text-muted-foreground">
      <Loader2 :size="24" class="animate-spin mr-2" /> 載入中…
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
    >
      <AlertCircle :size="16" class="shrink-0" />
      <span>{{ error }}</span>
    </div>

    <template v-else-if="order">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-foreground tracking-tight">
            {{ order.order_number }}
          </h1>
          <div class="flex flex-wrap items-center gap-3 mt-1 text-sm text-muted-foreground">
            <span>供應商：{{ order.supplier_name }}</span>
            <span v-if="order.supplier_code">（{{ order.supplier_code }}）</span>
            <span>訂單日期：{{ order.order_date }}</span>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="getStatus(order.status).class"
            >
              {{ getStatus(order.status).label }}
            </span>
          </div>
        </div>
        <div class="flex gap-2 shrink-0">
          <button
            v-if="isOpen"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 border border-amber-200 dark:border-amber-800 transition-colors"
            :disabled="isCancelling"
            @click="handleCancel"
          >
            <Loader2 v-if="isCancelling" :size="14" class="animate-spin" />
            <Ban v-else :size="14" />
            取消訂單
          </button>
          <button
            v-if="order.status === 'FULLY_RECEIVED'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-primary text-primary-foreground hover:opacity-90 transition-opacity"
            :disabled="isClosing"
            @click="handleClose"
          >
            <Loader2 v-if="isClosing" :size="14" class="animate-spin" />
            <Lock v-else :size="14" />
            結案
          </button>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">項目數</p>
          <p class="text-2xl font-bold text-foreground">{{ order.items.length }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">訂單金額</p>
          <p class="text-2xl font-bold text-foreground">{{ formatCurrency(order.total_amount) }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">到貨進度</p>
          <p class="text-2xl font-bold text-foreground">
            {{ order.total_received }} / {{ order.total_ordered }}
          </p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">預期交貨</p>
          <p class="text-lg font-bold text-foreground">{{ order.expected_delivery_date }}</p>
        </div>
      </div>

      <!-- Items -->
      <div class="rounded-xl border border-border bg-card overflow-hidden">
        <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
          <h2 class="text-sm font-medium text-foreground">訂單項目</h2>
          <button
            v-if="isOpen"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
            @click="showAddItem = !showAddItem"
          >
            <Plus :size="12" />
            新增項目
          </button>
        </div>

        <!-- Add item form -->
        <div v-if="showAddItem && isOpen" class="p-4 border-b border-border bg-muted/10 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div>
              <label class="text-xs text-muted-foreground">項次 *</label>
              <input
                v-model.number="newItemNumber"
                type="number"
                min="1"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">物料名稱 *</label>
              <input
                v-model="newMaterialName"
                type="text"
                placeholder="物料名稱"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">機型</label>
              <input
                v-model="newModelName"
                type="text"
                placeholder="例如 A123"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
            <div>
              <label class="text-xs text-muted-foreground">規格</label>
              <input
                v-model="newSpec"
                type="text"
                placeholder="選填"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">數量</label>
              <input
                v-model.number="newQty"
                type="number"
                min="1"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">單價</label>
              <input
                v-model.number="newUnitPrice"
                type="number"
                min="0"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">交期</label>
              <input
                v-model="newDeliveryDate"
                type="date"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>
          <div class="flex justify-end">
            <button
              :disabled="!newMaterialName.trim() || isAddingItem"
              class="flex items-center gap-1.5 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
              @click="handleAddItem"
            >
              <Loader2 v-if="isAddingItem" :size="14" class="animate-spin" />
              <Plus v-else :size="14" />
              加入
            </button>
          </div>
        </div>

        <!-- Empty -->
        <div
          v-if="order.items.length === 0"
          class="flex flex-col items-center py-12 text-muted-foreground"
        >
          <PackageOpen :size="36" class="mb-2 opacity-40" />
          <p class="text-sm">尚無訂單項目</p>
        </div>

        <!-- Items -->
        <div v-else class="divide-y divide-border">
          <div v-for="item in order.items" :key="item.id" class="p-5 space-y-3">
            <!-- Item header -->
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    class="text-xs text-muted-foreground font-mono bg-muted px-1.5 py-0.5 rounded"
                  >
                    #{{ item.item_number }}
                  </span>
                  <span class="font-medium text-foreground">{{ item.material_name }}</span>
                  <span
                    v-if="item.model_name"
                    class="text-xs text-muted-foreground bg-muted/60 px-1.5 py-0.5 rounded"
                  >
                    {{ item.model_name }}
                  </span>
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="getItemStatus(item.status).class"
                  >
                    {{ getItemStatus(item.status).label }}
                  </span>
                </div>
                <div class="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                  <span v-if="item.specification">規格：{{ item.specification }}</span>
                  <span>數量：{{ item.quantity }}</span>
                  <span>單價：{{ formatCurrency(item.unit_price) }}</span>
                  <span>小計：{{ formatCurrency(item.subtotal) }}</span>
                  <span v-if="item.delivery_date">交期：{{ item.delivery_date }}</span>
                </div>
              </div>
              <div class="flex gap-1 shrink-0">
                <button
                  v-if="isOpen"
                  class="flex items-center gap-1 px-2 py-1 rounded text-xs text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-blue-200 dark:border-blue-800 transition-colors"
                  @click="receivingItemId = receivingItemId === item.id ? null : item.id"
                >
                  <PackageCheck :size="12" />
                  到貨
                </button>
                <button
                  v-if="isOpen"
                  class="flex items-center gap-1 px-2 py-1 rounded text-xs text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 border border-amber-200 dark:border-amber-800 transition-colors"
                  @click="holdItemId = holdItemId === item.id ? null : item.id"
                >
                  <PauseCircle :size="12" />
                  Hold
                </button>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="flex items-center gap-3">
              <div class="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  class="h-full bg-green-500 rounded-full transition-all"
                  :style="{
                    width:
                      item.quantity > 0
                        ? `${Math.min(100, (item.received_quantity / item.quantity) * 100)}%`
                        : '0%',
                  }"
                />
              </div>
              <span class="text-xs text-muted-foreground shrink-0">
                到貨 {{ item.received_quantity }} / {{ item.quantity }}
              </span>
              <span v-if="item.active_hold_quantity > 0" class="text-xs text-amber-600 shrink-0">
                Hold {{ item.active_hold_quantity }}
              </span>
            </div>

            <!-- Receiving form -->
            <div
              v-if="receivingItemId === item.id"
              class="p-3 bg-blue-50/50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-800 space-y-2"
            >
              <p class="text-xs font-medium text-blue-700 dark:text-blue-400">登錄到貨紀錄</p>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div>
                  <label class="text-xs text-muted-foreground">到貨數量 *</label>
                  <input
                    v-model.number="recQty"
                    type="number"
                    min="1"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">到貨日期 *</label>
                  <input
                    v-model="recDate"
                    type="datetime-local"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">驗收人</label>
                  <input
                    v-model="recInspector"
                    type="text"
                    placeholder="選填"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">備註</label>
                  <input
                    v-model="recNote"
                    type="text"
                    placeholder="選填"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
              </div>
              <div class="flex justify-end">
                <button
                  :disabled="!recQty || !recDate || isAddingReceiving"
                  class="flex items-center gap-1 px-3 py-1.5 rounded-md bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  @click="handleAddReceiving(item)"
                >
                  <Loader2 v-if="isAddingReceiving" :size="12" class="animate-spin" />
                  確認登錄
                </button>
              </div>
            </div>

            <!-- Hold form -->
            <div
              v-if="holdItemId === item.id"
              class="p-3 bg-amber-50/50 dark:bg-amber-900/10 rounded-lg border border-amber-100 dark:border-amber-800 space-y-2"
            >
              <p class="text-xs font-medium text-amber-700 dark:text-amber-400">設定 On-Hold</p>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div>
                  <label class="text-xs text-muted-foreground">Hold 數量 *</label>
                  <input
                    v-model.number="holdQty"
                    type="number"
                    min="1"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">原因 *</label>
                  <input
                    v-model="holdReason"
                    type="text"
                    placeholder="Hold 原因"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">操作人 *</label>
                  <input
                    v-model="holdBy"
                    type="text"
                    placeholder="你的名字"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
              </div>
              <div class="flex justify-end">
                <button
                  :disabled="!holdQty || !holdReason.trim() || !holdBy.trim() || isAddingHold"
                  class="flex items-center gap-1 px-3 py-1.5 rounded-md bg-amber-600 text-white text-xs font-medium hover:bg-amber-700 disabled:opacity-50 transition-colors"
                  @click="handleAddHold(item)"
                >
                  <Loader2 v-if="isAddingHold" :size="12" class="animate-spin" />
                  確認設定
                </button>
              </div>
            </div>

            <!-- Receiving records -->
            <div v-if="item.receiving_records.length > 0" class="space-y-1">
              <p class="text-xs font-medium text-muted-foreground">到貨紀錄</p>
              <div class="grid gap-1">
                <div
                  v-for="rec in item.receiving_records"
                  :key="rec.id"
                  class="flex items-center gap-3 text-xs bg-green-50/50 dark:bg-green-900/10 px-3 py-1.5 rounded border border-green-100 dark:border-green-800"
                >
                  <PackageCheck :size="12" class="text-green-600 shrink-0" />
                  <span class="text-foreground">數量 {{ rec.received_quantity }}</span>
                  <span class="text-muted-foreground">{{ rec.received_date?.slice(0, 10) }}</span>
                  <span v-if="rec.inspector" class="text-muted-foreground"
                    >驗收人：{{ rec.inspector }}</span
                  >
                  <span v-if="rec.note" class="text-muted-foreground">{{ rec.note }}</span>
                </div>
              </div>
            </div>

            <!-- Holds -->
            <div v-if="item.holds.length > 0" class="space-y-1">
              <p class="text-xs font-medium text-muted-foreground">On-Hold 紀錄</p>
              <div class="grid gap-1">
                <div
                  v-for="hold in item.holds"
                  :key="hold.id"
                  class="flex items-center gap-3 text-xs px-3 py-1.5 rounded border"
                  :class="
                    hold.status === 'ACTIVE'
                      ? 'bg-amber-50/50 dark:bg-amber-900/10 border-amber-100 dark:border-amber-800'
                      : 'bg-gray-50 dark:bg-gray-800/30 border-gray-200 dark:border-gray-700'
                  "
                >
                  <PauseCircle
                    v-if="hold.status === 'ACTIVE'"
                    :size="12"
                    class="text-amber-600 shrink-0"
                  />
                  <PlayCircle v-else :size="12" class="text-gray-400 shrink-0" />
                  <span class="text-foreground">數量 {{ hold.hold_quantity }}</span>
                  <span class="text-muted-foreground">{{ hold.reason }}</span>
                  <span class="text-muted-foreground">by {{ hold.held_by }}</span>
                  <span v-if="hold.status === 'RELEASED'" class="text-green-600">已釋放</span>
                  <button
                    v-if="hold.status === 'ACTIVE' && isOpen"
                    class="ml-auto flex items-center gap-1 px-2 py-0.5 rounded text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 border border-green-200 dark:border-green-800 transition-colors"
                    :disabled="releasingHoldId === hold.id"
                    @click="handleReleaseHold(item, hold.id)"
                  >
                    <Loader2 v-if="releasingHoldId === hold.id" :size="10" class="animate-spin" />
                    <PlayCircle v-else :size="10" />
                    釋放
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="order.notes" class="rounded-xl border border-border bg-card p-4">
        <p class="text-xs text-muted-foreground mb-1">備註</p>
        <p class="text-sm text-foreground">{{ order.notes }}</p>
      </div>
    </template>
  </div>
</template>
