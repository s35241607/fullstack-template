<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { procurementApi, type ProcurementPlan } from '@/services/api'
  import { ArrowLeft, Plus, Trash2, Send, Loader2, AlertCircle, PackageOpen } from 'lucide-vue-next'
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

  const isDraft = computed(() => plan.value?.status === 'DRAFT')

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
      plan.value.total_amount = plan.value.items.reduce(
        (s, i) => s + i.quantity * i.estimated_unit_price,
        0,
      )
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
      plan.value.total_amount = plan.value.items.reduce(
        (s, i) => s + i.quantity * i.estimated_unit_price,
        0,
      )
      toast.success('已移除', { description: `「${name}」已移除。` })
    } catch (err) {
      toast.error('移除失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      removingId.value = null
    }
  }

  async function handleSubmit() {
    if (!plan.value) return
    isSubmitting.value = true
    try {
      plan.value = await procurementApi.submitPlan(plan.value.id)
      toast.success('已送審', { description: `「${plan.value.name}」已成功送審。` })
    } catch (err) {
      toast.error('送審失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
    } finally {
      isSubmitting.value = false
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
  <div class="space-y-6 max-w-4xl">
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
          <div class="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
            <span>預計採購日：{{ plan.planned_date }}</span>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="
                plan.status === 'DRAFT'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
              "
            >
              {{ plan.status === 'DRAFT' ? '草稿' : '已送審' }}
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            v-if="isDraft"
            class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity"
            :disabled="plan.items.length === 0 || isSubmitting"
            @click="handleSubmit"
          >
            <Loader2 v-if="isSubmitting" :size="14" class="animate-spin" />
            <Send v-else :size="14" />
            送審
          </button>
        </div>
      </div>

      <!-- Summary card -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">項目數</p>
          <p class="text-2xl font-bold text-foreground">{{ plan.items.length }}</p>
        </div>
        <div class="rounded-xl border border-border bg-card p-4">
          <p class="text-xs text-muted-foreground mb-1">預估總金額</p>
          <p class="text-2xl font-bold text-foreground">{{ formatCurrency(plan.total_amount) }}</p>
        </div>
      </div>

      <!-- Items table -->
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
        <table v-else class="w-full text-sm">
          <thead>
            <tr class="border-b border-border text-left text-muted-foreground">
              <th class="px-5 py-2 font-medium">設備名稱</th>
              <th class="px-5 py-2 font-medium">規格</th>
              <th class="px-5 py-2 font-medium text-right">數量</th>
              <th class="px-5 py-2 font-medium text-right">預估單價</th>
              <th class="px-5 py-2 font-medium text-right">小計</th>
              <th v-if="isDraft" class="px-5 py-2 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in plan.items"
              :key="item.id"
              class="border-b border-border/50 last:border-b-0 hover:bg-muted/30 transition-colors"
            >
              <td class="px-5 py-3 font-medium text-foreground">{{ item.equipment_name }}</td>
              <td class="px-5 py-3 text-muted-foreground">{{ item.specification || '—' }}</td>
              <td class="px-5 py-3 text-right text-muted-foreground">{{ item.quantity }}</td>
              <td class="px-5 py-3 text-right text-muted-foreground">
                {{ formatCurrency(item.estimated_unit_price) }}
              </td>
              <td class="px-5 py-3 text-right text-foreground font-medium">
                {{ formatCurrency(item.quantity * item.estimated_unit_price) }}
              </td>
              <td v-if="isDraft" class="px-5 py-3 text-right">
                <button
                  class="p-1.5 rounded-md text-destructive hover:bg-destructive/10 transition-colors"
                  title="移除"
                  :disabled="removingId === item.id"
                  @click="handleRemoveItem(item.id, item.equipment_name)"
                >
                  <Loader2 v-if="removingId === item.id" :size="14" class="animate-spin" />
                  <Trash2 v-else :size="14" />
                </button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="border-t border-border">
              <td class="px-5 py-3 font-medium text-foreground" colspan="4">合計</td>
              <td class="px-5 py-3 text-right font-bold text-foreground">
                {{ formatCurrency(plan.total_amount) }}
              </td>
              <td v-if="isDraft" />
            </tr>
          </tfoot>
        </table>
      </div>
    </template>
  </div>
</template>
