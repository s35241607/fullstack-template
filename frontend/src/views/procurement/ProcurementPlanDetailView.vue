<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { procurementApi, type ProcurementPlan } from '@/services/api'
  import {
    ArrowLeft,
    Plus,
    Trash2,
    Send,
    Loader2,
    AlertCircle,
    PackageOpen,
    FileUp,
    DollarSign,
    CheckCircle,
    ClipboardCheck,
    ArrowRight,
  } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'

  const route = useRoute()
  const router = useRouter()

  const plan = ref<ProcurementPlan | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  // Add item form
  const showAddForm = ref(false)
  const newEquipment = ref('')
  const newSpec = ref('')
  const newQty = ref(1)
  const newPrice = ref(0)
  const newNote = ref('')
  const isAdding = ref(false)
  const removingId = ref<string | null>(null)
  const isSubmitting = ref(false)
  const isWorkflowAction = ref(false)

  // Spec upload form - per item
  const specItemId = ref<string | null>(null)
  const specUrl = ref('')
  const specBy = ref('')
  const isUploadingSpec = ref(false)

  // Quote form - per item
  const quoteItemId = ref<string | null>(null)
  const quotePrice = ref(0)
  const quoteSupplier = ref('')
  const isSettingQuote = ref(false)

  const isDraft = computed(() => plan.value?.status === 'DRAFT')

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

  const itemStatusMap: Record<string, { label: string; class: string }> = {
    PENDING: {
      label: '待處理',
      class: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    },
    SPEC_UPLOADED: {
      label: '已上傳 SPEC',
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
  }

  function getStatus(s: string) {
    return statusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }

  function getItemStatus(s: string) {
    return itemStatusMap[s] ?? { label: s, class: 'bg-gray-100 text-gray-800' }
  }

  // Workflow steps for visual indicator
  const workflowSteps = [
    'DRAFT',
    'SUBMITTED',
    'EE_REVIEW',
    'QUOTED',
    'APPROVED',
    'BUDGET_SUBMITTED',
  ]
  const workflowLabels: Record<string, string> = {
    DRAFT: '草稿',
    SUBMITTED: '送審',
    EE_REVIEW: 'EE 審查',
    QUOTED: '報價',
    APPROVED: '核准',
    BUDGET_SUBMITTED: '送預算',
  }

  function stepIndex(status: string) {
    return workflowSteps.indexOf(status)
  }

  async function loadPlan() {
    isLoading.value = true
    error.value = null
    try {
      plan.value = await procurementApi.getPlan(route.params.id as string)
    } catch {
      error.value = '無法載入採購計畫'
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadPlan)

  async function handleAddItem() {
    if (!newEquipment.value.trim() || !plan.value) return
    isAdding.value = true
    try {
      const item = await procurementApi.addItem(plan.value.id, {
        equipment_name: newEquipment.value.trim(),
        specification: newSpec.value.trim(),
        quantity: newQty.value,
        estimated_unit_price: newPrice.value,
        note: newNote.value.trim(),
      })
      plan.value.items.push(item)
      plan.value.total_amount = plan.value.items.reduce((s, i) => s + i.subtotal, 0)
      toast.success('已新增項目', { description: `「${item.equipment_name}」已加入。` })
      newEquipment.value = ''
      newSpec.value = ''
      newQty.value = 1
      newPrice.value = 0
      newNote.value = ''
      showAddForm.value = false
    } catch (err) {
      toast.error('新增失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isAdding.value = false
    }
  }

  async function handleRemoveItem(itemId: string, name: string) {
    if (!plan.value) return
    removingId.value = itemId
    try {
      await procurementApi.removeItem(plan.value.id, itemId)
      plan.value.items = plan.value.items.filter((i) => i.id !== itemId)
      plan.value.total_amount = plan.value.items.reduce((s, i) => s + i.subtotal, 0)
      toast.success('已移除', { description: `「${name}」已移除。` })
    } catch (err) {
      toast.error('移除失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      removingId.value = null
    }
  }

  async function handleWorkflowAction(action: string) {
    if (!plan.value) return
    isWorkflowAction.value = true
    try {
      let updated: ProcurementPlan
      switch (action) {
        case 'submit':
          updated = await procurementApi.submitPlan(plan.value.id)
          break
        case 'ee-review':
          updated = await procurementApi.sendToEeReview(plan.value.id)
          break
        case 'mark-quoted':
          updated = await procurementApi.markQuoted(plan.value.id)
          break
        case 'approve':
          updated = await procurementApi.approvePlan(plan.value.id)
          break
        case 'submit-budget':
          updated = await procurementApi.submitToBudget(plan.value.id)
          break
        default:
          return
      }
      plan.value = updated
      toast.success('狀態已更新')
    } catch (err) {
      toast.error('操作失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isWorkflowAction.value = false
    }
  }

  async function handleUploadSpec(itemId: string) {
    if (!plan.value || !specUrl.value.trim() || !specBy.value.trim()) return
    isUploadingSpec.value = true
    try {
      const updated = await procurementApi.uploadSpec(plan.value.id, itemId, {
        file_url: specUrl.value.trim(),
        uploaded_by: specBy.value.trim(),
      })
      const idx = plan.value.items.findIndex((i) => i.id === itemId)
      if (idx !== -1) plan.value.items[idx] = updated
      toast.success('SPEC 已上傳')
      specItemId.value = null
      specUrl.value = ''
      specBy.value = ''
    } catch (err) {
      toast.error('上傳失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isUploadingSpec.value = false
    }
  }

  async function handleSetQuote(itemId: string) {
    if (!plan.value || !quoteSupplier.value.trim()) return
    isSettingQuote.value = true
    try {
      const updated = await procurementApi.setQuote(plan.value.id, itemId, {
        quoted_unit_price: quotePrice.value,
        supplier_name: quoteSupplier.value.trim(),
      })
      const idx = plan.value.items.findIndex((i) => i.id === itemId)
      if (idx !== -1) plan.value.items[idx] = updated
      toast.success('報價已設定')
      quoteItemId.value = null
      quotePrice.value = 0
      quoteSupplier.value = ''
    } catch (err) {
      toast.error('設定失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isSettingQuote.value = false
    }
  }

  function formatCurrency(n: number) {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      maximumFractionDigits: 0,
    }).format(n)
  }
</script>

<template>
  <div class="space-y-6 max-w-5xl">
    <!-- Back -->
    <button
      class="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      @click="router.push({ name: 'procurement-plans' })"
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

    <template v-else-if="plan">
      <!-- Plan header -->
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-foreground tracking-tight">{{ plan.name }}</h1>
          <div class="flex flex-wrap items-center gap-3 mt-1 text-sm text-muted-foreground">
            <span>預計採購日：{{ plan.planned_date }}</span>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="getStatus(plan.status).class"
            >
              {{ getStatus(plan.status).label }}
            </span>
          </div>
        </div>
        <div class="flex gap-2 shrink-0">
          <!-- Workflow action buttons -->
          <button
            v-if="plan.status === 'DRAFT'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            :disabled="plan.items.length === 0 || isWorkflowAction"
            @click="handleWorkflowAction('submit')"
          >
            <Loader2 v-if="isWorkflowAction" :size="14" class="animate-spin" />
            <Send v-else :size="14" />
            送審
          </button>
          <button
            v-if="plan.status === 'SUBMITTED'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
            :disabled="isWorkflowAction"
            @click="handleWorkflowAction('ee-review')"
          >
            <Loader2 v-if="isWorkflowAction" :size="14" class="animate-spin" />
            <ClipboardCheck v-else :size="14" />
            送 EE 審查
          </button>
          <button
            v-if="plan.status === 'EE_REVIEW'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-cyan-600 text-white hover:bg-cyan-700 disabled:opacity-50 transition-colors"
            :disabled="isWorkflowAction"
            @click="handleWorkflowAction('mark-quoted')"
          >
            <Loader2 v-if="isWorkflowAction" :size="14" class="animate-spin" />
            <DollarSign v-else :size="14" />
            標記已報價
          </button>
          <button
            v-if="plan.status === 'QUOTED'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
            :disabled="isWorkflowAction"
            @click="handleWorkflowAction('approve')"
          >
            <Loader2 v-if="isWorkflowAction" :size="14" class="animate-spin" />
            <CheckCircle v-else :size="14" />
            核准
          </button>
          <button
            v-if="plan.status === 'APPROVED'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            :disabled="isWorkflowAction"
            @click="handleWorkflowAction('submit-budget')"
          >
            <Loader2 v-if="isWorkflowAction" :size="14" class="animate-spin" />
            <ArrowRight v-else :size="14" />
            送預算系統
          </button>
        </div>
      </div>

      <!-- Workflow progress -->
      <div class="rounded-xl border border-border bg-card p-4">
        <div class="flex items-center justify-between">
          <div
            v-for="(step, idx) in workflowSteps"
            :key="step"
            class="flex items-center"
            :class="idx < workflowSteps.length - 1 ? 'flex-1' : ''"
          >
            <div class="flex flex-col items-center">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
                :class="
                  stepIndex(plan.status) >= idx
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                "
              >
                {{ idx + 1 }}
              </div>
              <span class="text-[10px] mt-1 text-muted-foreground whitespace-nowrap">
                {{ workflowLabels[step] }}
              </span>
            </div>
            <div
              v-if="idx < workflowSteps.length - 1"
              class="flex-1 h-0.5 mx-2 mt-[-12px] transition-colors"
              :class="stepIndex(plan.status) > idx ? 'bg-primary' : 'bg-muted'"
            />
          </div>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">項目數</p>
          <p class="text-2xl font-bold text-foreground">{{ plan.items.length }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">預估總金額</p>
          <p class="text-2xl font-bold text-foreground">{{ formatCurrency(plan.total_amount) }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">最終報價總額</p>
          <p class="text-2xl font-bold text-foreground">
            {{ formatCurrency(plan.items.reduce((s, i) => s + i.final_subtotal, 0)) }}
          </p>
        </div>
      </div>

      <!-- Items -->
      <div class="rounded-xl border border-border bg-card overflow-hidden">
        <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
          <h2 class="text-sm font-medium text-foreground">設備項目</h2>
          <button
            v-if="isDraft"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
            @click="showAddForm = !showAddForm"
          >
            <Plus :size="12" />
            新增項目
          </button>
        </div>

        <!-- Add item form -->
        <div v-if="showAddForm && isDraft" class="p-4 border-b border-border bg-muted/10 space-y-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input
              v-model="newEquipment"
              type="text"
              placeholder="設備名稱 *"
              class="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <input
              v-model="newSpec"
              type="text"
              placeholder="規格"
              class="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
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
              <label class="text-xs text-muted-foreground">預估單價</label>
              <input
                v-model.number="newPrice"
                type="number"
                min="0"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground">備註</label>
              <input
                v-model="newNote"
                type="text"
                placeholder="選填"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>
          <div class="flex justify-end">
            <button
              :disabled="!newEquipment.trim() || isAdding"
              class="flex items-center gap-1.5 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
              @click="handleAddItem"
            >
              <Loader2 v-if="isAdding" :size="14" class="animate-spin" />
              <Plus v-else :size="14" />
              加入
            </button>
          </div>
        </div>

        <!-- Empty -->
        <div
          v-if="plan.items.length === 0"
          class="flex flex-col items-center py-12 text-muted-foreground"
        >
          <PackageOpen :size="36" class="mb-2 opacity-40" />
          <p class="text-sm">尚無設備項目</p>
        </div>

        <!-- Items list -->
        <div v-else class="divide-y divide-border">
          <div v-for="item in plan.items" :key="item.id" class="p-5 space-y-3">
            <!-- Item header -->
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-medium text-foreground">{{ item.equipment_name }}</span>
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="getItemStatus(item.item_status).class"
                  >
                    {{ getItemStatus(item.item_status).label }}
                  </span>
                </div>
                <div class="flex flex-wrap items-center gap-4 mt-1 text-xs text-muted-foreground">
                  <span v-if="item.specification">規格：{{ item.specification }}</span>
                  <span>數量：{{ item.quantity }}</span>
                  <span>預估單價：{{ formatCurrency(item.estimated_unit_price) }}</span>
                  <span>預估小計：{{ formatCurrency(item.subtotal) }}</span>
                  <span v-if="item.quoted_unit_price !== null" class="text-cyan-600 font-medium">
                    報價單價：{{ formatCurrency(item.quoted_unit_price) }}
                  </span>
                  <span v-if="item.quoted_unit_price !== null" class="text-cyan-600 font-medium">
                    最終小計：{{ formatCurrency(item.final_subtotal) }}
                  </span>
                  <span v-if="item.supplier_name" class="text-muted-foreground">
                    供應商：{{ item.supplier_name }}
                  </span>
                </div>
              </div>
              <div class="flex gap-1 shrink-0">
                <!-- SPEC Upload button -->
                <button
                  v-if="['EE_REVIEW'].includes(plan.status) && item.item_status === 'PENDING'"
                  class="flex items-center gap-1 px-2 py-1 rounded text-xs text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 border border-purple-200 dark:border-purple-800 transition-colors"
                  @click="specItemId = specItemId === item.id ? null : item.id"
                >
                  <FileUp :size="12" />
                  上傳 SPEC
                </button>
                <!-- Set Quote button -->
                <button
                  v-if="
                    ['EE_REVIEW', 'QUOTED'].includes(plan.status) &&
                    ['PENDING', 'SPEC_UPLOADED'].includes(item.item_status)
                  "
                  class="flex items-center gap-1 px-2 py-1 rounded text-xs text-cyan-600 hover:bg-cyan-50 dark:hover:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-800 transition-colors"
                  @click="quoteItemId = quoteItemId === item.id ? null : item.id"
                >
                  <DollarSign :size="12" />
                  設定報價
                </button>
                <!-- Remove button (draft only) -->
                <button
                  v-if="isDraft"
                  class="p-1.5 rounded-md text-destructive hover:bg-destructive/10 transition-colors"
                  title="移除"
                  :disabled="removingId === item.id"
                  @click="handleRemoveItem(item.id, item.equipment_name)"
                >
                  <Loader2 v-if="removingId === item.id" :size="14" class="animate-spin" />
                  <Trash2 v-else :size="14" />
                </button>
              </div>
            </div>

            <!-- SPEC info -->
            <div
              v-if="item.spec_file_url"
              class="flex items-center gap-2 text-xs bg-purple-50/50 dark:bg-purple-900/10 px-3 py-1.5 rounded border border-purple-100 dark:border-purple-800"
            >
              <FileUp :size="12" class="text-purple-600 shrink-0" />
              <span class="text-foreground">SPEC：{{ item.spec_file_url }}</span>
              <span v-if="item.spec_uploaded_by" class="text-muted-foreground"
                >by {{ item.spec_uploaded_by }}</span
              >
              <span v-if="item.spec_uploaded_at" class="text-muted-foreground">{{
                item.spec_uploaded_at?.slice(0, 10)
              }}</span>
            </div>

            <!-- SPEC upload form -->
            <div
              v-if="specItemId === item.id"
              class="p-3 bg-purple-50/50 dark:bg-purple-900/10 rounded-lg border border-purple-100 dark:border-purple-800 space-y-2"
            >
              <p class="text-xs font-medium text-purple-700 dark:text-purple-400">上傳 SPEC 檔案</p>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-muted-foreground">檔案連結 *</label>
                  <input
                    v-model="specUrl"
                    type="text"
                    placeholder="https://..."
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">上傳人 *</label>
                  <input
                    v-model="specBy"
                    type="text"
                    placeholder="你的名字"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
              </div>
              <div class="flex justify-end">
                <button
                  :disabled="!specUrl.trim() || !specBy.trim() || isUploadingSpec"
                  class="flex items-center gap-1 px-3 py-1.5 rounded-md bg-purple-600 text-white text-xs font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  @click="handleUploadSpec(item.id)"
                >
                  <Loader2 v-if="isUploadingSpec" :size="12" class="animate-spin" />
                  確認上傳
                </button>
              </div>
            </div>

            <!-- Quote form -->
            <div
              v-if="quoteItemId === item.id"
              class="p-3 bg-cyan-50/50 dark:bg-cyan-900/10 rounded-lg border border-cyan-100 dark:border-cyan-800 space-y-2"
            >
              <p class="text-xs font-medium text-cyan-700 dark:text-cyan-400">設定供應商報價</p>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-muted-foreground">報價單價 *</label>
                  <input
                    v-model.number="quotePrice"
                    type="number"
                    min="0"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
                <div>
                  <label class="text-xs text-muted-foreground">供應商名稱 *</label>
                  <input
                    v-model="quoteSupplier"
                    type="text"
                    placeholder="供應商名稱"
                    class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
              </div>
              <div class="flex justify-end">
                <button
                  :disabled="!quoteSupplier.trim() || isSettingQuote"
                  class="flex items-center gap-1 px-3 py-1.5 rounded-md bg-cyan-600 text-white text-xs font-medium hover:bg-cyan-700 disabled:opacity-50 transition-colors"
                  @click="handleSetQuote(item.id)"
                >
                  <Loader2 v-if="isSettingQuote" :size="12" class="animate-spin" />
                  確認設定
                </button>
              </div>
            </div>

            <!-- Note -->
            <p v-if="item.note" class="text-xs text-muted-foreground">備註：{{ item.note }}</p>
          </div>
        </div>

        <!-- Footer total -->
        <div
          v-if="plan.items.length > 0"
          class="px-5 py-3 border-t border-border bg-muted/30 flex justify-between items-center text-sm"
        >
          <span class="font-medium text-foreground">合計</span>
          <span class="font-bold text-foreground">{{ formatCurrency(plan.total_amount) }}</span>
        </div>
      </div>
    </template>
  </div>
</template>
