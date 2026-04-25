<script setup lang="ts">
import { ref } from 'vue'
import { cn } from '@/lib/utils'
import { AppSelect, AppAutoComplete, AppComboBox, AppTable, AppAdvancedTable } from '@/components/common'
import type { SelectOption, AutoCompleteOption, ComboBoxOption, SimpleTableColumn, DataTableColumn } from '@/components/common'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'

// ── Select Demo ──────────────────────────────────────────────────────────────
const selectBasic = ref('')
const selectRich = ref('kelly')
const basicOptions: SelectOption[] = [
  { label: 'High Priority', value: 'high' },
  { label: 'Medium Priority', value: 'medium' },
  { label: 'Low Priority', value: 'low' },
  { label: 'Archived', value: 'archived', disabled: true },
]
const richOptions: SelectOption[] = [
  { label: 'Kelly Lin', value: 'kelly', description: 'Senior Planner', avatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Kelly' },
  { label: 'Ryan Wu', value: 'ryan', description: 'Logistics Manager', avatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Ryan' },
  { label: 'Ariel Chen', value: 'ariel', description: 'Procurement Specialist', avatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Ariel' },
]

// ── AutoComplete Demo ────────────────────────────────────────────────────────
const autoCompleteValue = ref('')
const projectOptions: AutoCompleteOption[] = [
  { label: 'Project Alpha — 先進封裝', value: 'alpha' },
  { label: 'Project Beta — 晶片設計', value: 'beta' },
  { label: 'Project Gamma — 電源管理', value: 'gamma' },
  { label: 'Project Delta — 被動元件', value: 'delta' },
  { label: 'Project Epsilon — 模組整合', value: 'epsilon' },
]

// ── ComboBox Demo ────────────────────────────────────────────────────────────
const comboValue = ref('')
const createdTags = ref<string[]>([])
const tagOptions = ref<ComboBoxOption[]>([
  { label: 'Frontend', value: 'frontend' },
  { label: 'Backend', value: 'backend' },
  { label: 'DevOps', value: 'devops' },
  { label: 'Design', value: 'design' },
  { label: 'QA', value: 'qa' },
])
function handleCreateTag(tag: string) {
  const v = tag.toLowerCase().replace(/\s+/g, '-')
  if (!tagOptions.value.some((o) => o.value === v)) {
    tagOptions.value.push({ label: tag, value: v })
    createdTags.value.push(tag)
  }
}

// ── Simple Table Demo ────────────────────────────────────────────────────────
const simpleColumns: SimpleTableColumn[] = [
  { key: 'id', header: 'ID', class: 'w-[80px]' },
  { key: 'name', header: '名稱' },
  { key: 'email', header: 'Email' },
  { key: 'role', header: '角色', align: 'center' },
]
const simpleData = [
  { id: '1', name: 'Alice Johnson', email: 'alice@example.com', role: 'Admin' },
  { id: '2', name: 'Bob Smith', email: 'bob@example.com', role: 'User' },
  { id: '3', name: 'Charlie Brown', email: 'charlie@example.com', role: 'User' },
]

// ── Advanced Table Demo ──────────────────────────────────────────────────────
const advancedColumns: DataTableColumn[] = [
  { key: 'id', header: 'ID', width: 100, frozen: true, sortable: true },
  { key: 'name', header: '品項名稱', width: 200, frozen: true, editable: true, sortable: true },
  { key: 'category', header: '分類', width: 120, sortable: true },
  { key: 'stock', header: '庫存', width: 90, align: 'right', editable: true, sortable: true },
  { key: 'price', header: '單價', width: 100, align: 'right', editable: true, sortable: true },
  { key: 'supplier', header: '供應商', width: 160, editable: true, sortable: true },
  { key: 'warehouse', header: '倉庫', width: 100, editable: true },
  { key: 'lastUpdate', header: '更新日期', width: 120, sortable: true },
]

const inventoryData = ref<Record<string, unknown>[]>([
  { id: 'ITM-001', name: '高頻電感 10uH', category: '被動元件', stock: 1250, price: 45.5, supplier: '鴻海 (Foxconn)', warehouse: 'W-A1', lastUpdate: '2026-04-20' },
  { id: 'ITM-002', name: 'MCU-32 微控制器', category: 'IC', stock: 4200, price: 120.0, supplier: '台積電 (TSMC)', warehouse: 'W-B2', lastUpdate: '2026-04-21' },
  { id: 'ITM-003', name: 'MLCC 0402 電容', category: '被動元件', stock: 18000, price: 0.15, supplier: '日月光 (ASE)', warehouse: 'W-A1', lastUpdate: '2026-04-18' },
  { id: 'ITM-004', name: 'PMIC 電源管理晶片', category: 'IC', stock: 960, price: 85.0, supplier: '德州儀器 (TI)', warehouse: 'W-C3', lastUpdate: '2026-04-22' },
  { id: 'ITM-005', name: '散熱模組 (鋁心)', category: '機構件', stock: 450, price: 12.5, supplier: 'CoolerMaster', warehouse: 'W-D1', lastUpdate: '2026-04-15' },
  { id: 'ITM-006', name: '石英振盪器 24MHz', category: '被動元件', stock: 3200, price: 2.4, supplier: 'TXC', warehouse: 'W-A2', lastUpdate: '2026-04-19' },
  { id: 'ITM-007', name: 'USB-C 連接器', category: '連接器', stock: 5600, price: 8.2, supplier: '鴻海 (Foxconn)', warehouse: 'W-B1', lastUpdate: '2026-04-23' },
  { id: 'ITM-008', name: 'LED 指示燈 (綠)', category: '光電', stock: 12000, price: 0.08, supplier: '億光 (Everlight)', warehouse: 'W-A1', lastUpdate: '2026-04-20' },
])

const isLoading = ref(false)
const editLog = ref<string[]>([])

function simulateLoading() { isLoading.value = true; setTimeout(() => { isLoading.value = false }, 1500) }
function handleCellUpdate(p: { row: Record<string, unknown>; key: string; oldValue: unknown; newValue: string }) {
  p.row[p.key] = p.newValue
  editLog.value.unshift(`[${p.row.id}] ${p.key}: "${p.oldValue}" → "${p.newValue}"`)
  if (editLog.value.length > 5) editLog.value.pop()
}
function handleRowsReorder(d: Record<string, unknown>[]) { inventoryData.value = d }

function stockColor(v: unknown) {
  const n = Number(v)
  if (n <= 1000) return 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-950'
  if (n <= 5000) return 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-950'
  return 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-950'
}
</script>

<template>
  <div class="flex flex-col gap-6 w-full">
    <div class="flex flex-col gap-1">
      <h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
        {{ $t('demo.title', '共用元件展示') }}
      </h1>
      <p class="text-xs text-muted-foreground sm:text-sm">
        {{ $t('demo.subtitle', '使用 shadcn-vue 原生元件封裝，符合 Vue 3 + TypeScript 規範。') }}
      </p>
    </div>

    <Tabs default-value="selects" class="flex flex-col gap-6">
      <TabsList>
        <TabsTrigger value="selects">{{ $t('demo.tabs.selection') }}</TabsTrigger>
        <TabsTrigger value="tables">{{ $t('demo.tabs.table') }}</TabsTrigger>
      </TabsList>

      <!-- ═══ Selection Tab ═══ -->
      <TabsContent value="selects" class="flex flex-col gap-8">
        <Card>
          <CardHeader>
            <CardTitle>{{ $t('demo.select.title') }}</CardTitle>
            <CardDescription>{{ $t('demo.select.desc') }}</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium">{{ $t('demo.select.basicLabel') }}</label>
                <AppSelect v-model="selectBasic" :options="basicOptions" :placeholder="$t('demo.select.placeholder')" group-label="Priority" class="w-full" />
                <p class="text-xs text-muted-foreground">Selected: <code class="font-mono text-primary">{{ selectBasic || '(none)' }}</code></p>
              </div>
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium">{{ $t('demo.select.richLabel') }}</label>
                <AppSelect v-model="selectRich" :options="richOptions" :placeholder="$t('demo.select.richPlaceholder')" group-label="Team Members" class="w-full" />
                <p class="text-xs text-muted-foreground">Selected: <code class="font-mono text-primary">{{ selectRich || '(none)' }}</code></p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{{ $t('demo.autoComplete.title') }}</CardTitle>
            <CardDescription>{{ $t('demo.autoComplete.desc') }}</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="max-w-sm flex flex-col gap-2">
              <label class="text-sm font-medium">{{ $t('demo.autoComplete.label') }}</label>
              <AppAutoComplete v-model="autoCompleteValue" :options="projectOptions" :placeholder="$t('demo.autoComplete.placeholder')" :search-placeholder="$t('demo.autoComplete.searchPlaceholder')" class="w-full" />
              <p class="text-xs text-muted-foreground">Selected: <code class="font-mono text-primary">{{ autoCompleteValue || '(none)' }}</code></p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{{ $t('demo.comboBox.title') }}</CardTitle>
            <CardDescription>{{ $t('demo.comboBox.desc') }}</CardDescription>
          </CardHeader>
          <CardContent class="flex flex-col gap-4">
            <div class="max-w-sm flex flex-col gap-2">
              <label class="text-sm font-medium">{{ $t('demo.comboBox.label') }}</label>
              <AppComboBox v-model="comboValue" :options="tagOptions" :placeholder="$t('demo.comboBox.placeholder')" class="w-full" @create="handleCreateTag" />
              <p class="text-xs text-muted-foreground">Value: <code class="font-mono text-primary">{{ comboValue || '(empty)' }}</code></p>
            </div>
            <div v-if="createdTags.length" class="flex flex-col gap-1">
              <p class="text-xs font-medium text-muted-foreground">{{ $t('demo.comboBox.newTags') }}</p>
              <div class="flex flex-wrap gap-1.5">
                <Badge v-for="t in createdTags" :key="t" variant="secondary">{{ t }}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- ═══ Table Tab ═══ -->
      <TabsContent value="tables" class="flex flex-col gap-8">
        <Card>
          <CardHeader>
            <CardTitle>{{ $t('demo.table.simpleTitle') }}</CardTitle>
            <CardDescription>{{ $t('demo.table.simpleDesc') }}</CardDescription>
          </CardHeader>
          <CardContent>
            <AppTable :columns="simpleColumns" :data="simpleData">
              <template #cell-role="{ value }"><Badge variant="secondary">{{ value }}</Badge></template>
            </AppTable>
          </CardContent>
        </Card>

        <Separator />

        <Card>
          <CardHeader class="flex flex-row items-start justify-between gap-4">
            <div class="flex flex-col gap-1">
              <CardTitle>{{ $t('demo.table.advancedTitle') }}</CardTitle>
              <CardDescription>{{ $t('demo.table.advancedDesc') }}</CardDescription>
            </div>
            <button class="shrink-0 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent" @click="simulateLoading">
              {{ $t('demo.table.simulateLoading') }}
            </button>
          </CardHeader>
          <CardContent class="flex flex-col gap-3">
            <div class="flex flex-wrap items-center gap-1.5">
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.nav') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.click') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.edit') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.check') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.copy') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.sort') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.reorderCol') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.reorderRow') }}</Badge>
              <Badge variant="outline" class="text-xs">{{ $t('demo.table.features.resize') }}</Badge>
            </div>

            <AppAdvancedTable
              :columns="advancedColumns"
              :data="inventoryData"
              :loading="isLoading"
              group-by="category"
              searchable
              @cell-update="handleCellUpdate"
              @rows-reorder="handleRowsReorder"
            >
              <template #cell-stock="{ value }">
                <Badge variant="outline" :class="cn('tabular-nums font-semibold', stockColor(value))">
                  {{ Number(value).toLocaleString() }}
                </Badge>
              </template>
              <template #cell-price="{ value }">
                <span class="tabular-nums font-medium">${{ Number(value).toFixed(2) }}</span>
              </template>
              <template #expanded-row="{ row }">
                <div class="grid gap-3 sm:grid-cols-2">
                  <div class="rounded-md border p-3 flex flex-col gap-1">
                    <p class="mb-1 text-xs font-semibold text-muted-foreground">品項資訊</p>
                    <dl class="flex flex-col gap-1 text-sm">
                      <div class="flex justify-between"><dt class="text-muted-foreground">編號</dt><dd class="font-mono">{{ row.id }}</dd></div>
                      <div class="flex justify-between"><dt class="text-muted-foreground">供應商</dt><dd>{{ row.supplier }}</dd></div>
                      <div class="flex justify-between"><dt class="text-muted-foreground">倉庫</dt><dd>{{ row.warehouse }}</dd></div>
                    </dl>
                  </div>
                  <div class="rounded-md border p-3 flex flex-col gap-1">
                    <p class="mb-1 text-xs font-semibold text-muted-foreground">庫存狀態</p>
                    <dl class="flex flex-col gap-1 text-sm">
                      <div class="flex justify-between"><dt class="text-muted-foreground">庫存</dt><dd class="tabular-nums font-semibold">{{ Number(row.stock).toLocaleString() }}</dd></div>
                      <div class="flex justify-between"><dt class="text-muted-foreground">單價</dt><dd class="tabular-nums">${{ Number(row.price).toFixed(2) }}</dd></div>
                      <div class="flex justify-between"><dt class="text-muted-foreground">更新</dt><dd>{{ row.lastUpdate }}</dd></div>
                    </dl>
                  </div>
                </div>
              </template>
            </AppAdvancedTable>

            <div v-if="editLog.length" class="rounded-md border bg-muted/20 p-3 flex flex-col gap-1">
              <p class="mb-1 text-xs font-semibold text-muted-foreground">{{ $t('demo.table.editLog') }}</p>
              <ul class="flex flex-col gap-0.5">
                <li v-for="(l, i) in editLog" :key="i" class="font-mono text-xs text-foreground/60">{{ l }}</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>
