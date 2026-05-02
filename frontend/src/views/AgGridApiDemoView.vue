<script setup lang="ts">
  import { computed, onMounted, reactive, ref, watch } from 'vue'
  import type { FilterChangedEvent, GridApi, ICellRendererParams, SortChangedEvent } from 'ag-grid-community'
  import {
    AgGrid,
    SearchableSelectEditor,
    type AgGridColumnDef,
    type AgGridOptions,
    type AgGridRowData,
  } from '@/components/ui/ag-grid'
  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import { Input } from '@/components/ui/input'
  import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from '@/components/ui/select'
  import {
    agGridMockApi,
    type InventoryFilterModel,
    type InventoryLookupOptions,
    type InventorySortModelItem,
  } from '@/services/agGridMockApi'
  import { Database, FilterX, RefreshCw, Search } from 'lucide-vue-next'

  const emptyLookupOptions: InventoryLookupOptions = {
    categories: [],
    statuses: [],
    suppliers: [],
    warehouses: [],
  }

  const gridRef = ref<{ gridApi: { value: GridApi<AgGridRowData> | null } } | null>(null)
  const rowData = ref<AgGridRowData[]>([])
  const lookupOptions = ref<InventoryLookupOptions>(emptyLookupOptions)
  const page = ref(1)
  const pageSize = ref('20')
  const total = ref(0)
  const quickSearch = ref('')
  const isLoadingRows = ref(false)
  const isLoadingLookups = ref(false)
  const loadedAt = ref('')
  const sortModel = ref<InventorySortModelItem[]>([])
  const filterModel = ref<InventoryFilterModel>({})

  const dropdownFilters = reactive({
    category: 'all',
    supplier: 'all',
    status: 'all',
    warehouse: 'all',
  })

  let rowRequestId = 0

  const pageSizeNumber = computed(() => Number(pageSize.value))
  const totalPages = computed(() => Math.max(Math.ceil(total.value / pageSizeNumber.value), 1))
  const pageStart = computed(() => (total.value === 0 ? 0 : (page.value - 1) * pageSizeNumber.value + 1))
  const pageEnd = computed(() => Math.min(page.value * pageSizeNumber.value, total.value))
  const hasActiveQuery = computed(
    () =>
      Boolean(quickSearch.value.trim()) ||
      dropdownFilters.category !== 'all' ||
      dropdownFilters.supplier !== 'all' ||
      dropdownFilters.status !== 'all' ||
      dropdownFilters.warehouse !== 'all' ||
      Object.keys(filterModel.value).length > 0 ||
      sortModel.value.length > 0,
  )

  const formatNumber = (value: number) => value.toLocaleString('zh-TW')
  const formatCurrency = (value: unknown) => `$${Number(value ?? 0).toLocaleString('zh-TW')}`

  const statusClassMap: Record<string, string> = {
    可用: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
    低庫存: 'bg-amber-500/10 text-amber-700 dark:text-amber-300',
    待補貨: 'bg-blue-500/10 text-blue-700 dark:text-blue-300',
    鎖定: 'bg-rose-500/10 text-rose-700 dark:text-rose-300',
    驗收中: 'bg-violet-500/10 text-violet-700 dark:text-violet-300',
  }

  const renderStatus = (params: ICellRendererParams<AgGridRowData>) => {
    const value = String(params.value ?? '')
    const className = statusClassMap[value] ?? 'bg-muted text-muted-foreground'
    return `<span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${className}">${value}</span>`
  }

  const renderStock = (params: ICellRendererParams<AgGridRowData>) => {
    const stock = Number(params.value ?? 0)
    const reserved = Number(params.data?.reserved ?? 0)
    const open = Math.max(stock - reserved, 0)
    return `<div class="flex flex-col items-end leading-tight"><span class="font-mono font-semibold">${formatNumber(stock)}</span><span class="text-[11px] text-muted-foreground">open ${formatNumber(open)}</span></div>`
  }

  const columnDefs = computed<AgGridColumnDef[]>(() => [
    {
      field: 'id',
      headerName: 'ID',
      width: 110,
      pinned: 'left',
      filter: 'agTextColumnFilter',
      editable: false,
      cellClass: 'font-mono text-xs text-muted-foreground',
    },
    {
      field: 'itemCode',
      headerName: '料號',
      width: 140,
      filter: 'agTextColumnFilter',
      cellClass: 'font-mono text-xs',
    },
    {
      field: 'itemName',
      headerName: '品項名稱',
      minWidth: 220,
      filter: 'agTextColumnFilter',
    },
    {
      field: 'category',
      headerName: '分類',
      width: 130,
      filter: 'agSetColumnFilter',
      filterParams: { values: lookupOptions.value.categories },
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: { values: lookupOptions.value.categories },
    },
    {
      field: 'supplier',
      headerName: '供應商',
      minWidth: 170,
      filter: 'agSetColumnFilter',
      filterParams: { values: lookupOptions.value.suppliers },
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: { values: lookupOptions.value.suppliers },
    },
    {
      field: 'warehouse',
      headerName: '倉庫',
      width: 110,
      filter: 'agSetColumnFilter',
      filterParams: { values: lookupOptions.value.warehouses },
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: { values: lookupOptions.value.warehouses },
    },
    {
      field: 'status',
      headerName: '狀態',
      width: 120,
      filter: 'agSetColumnFilter',
      filterParams: { values: lookupOptions.value.statuses },
      cellRenderer: renderStatus,
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: { values: lookupOptions.value.statuses },
    },
    {
      field: 'stock',
      headerName: '庫存',
      width: 130,
      filter: 'agNumberColumnFilter',
      cellRenderer: renderStock,
      cellClass: 'text-right',
    },
    {
      field: 'unitPrice',
      headerName: '單價',
      width: 120,
      filter: 'agNumberColumnFilter',
      valueFormatter: (params) => formatCurrency(params.value),
      cellClass: 'font-mono text-right',
    },
    {
      field: 'buyer',
      headerName: '採購',
      width: 130,
      filter: 'agTextColumnFilter',
    },
    {
      field: 'lastUpdate',
      headerName: '更新日期',
      width: 130,
      filter: 'agDateColumnFilter',
      cellClass: 'font-mono text-xs text-muted-foreground',
    },
  ])

  const gridOptions = computed<AgGridOptions>(() => ({
    suppressPaginationPanel: true,
    onSortChanged: handleSortChanged,
    onFilterChanged: handleFilterChanged,
  }))

  const getGridApi = () => gridRef.value?.gridApi.value ?? null

  const loadRows = async () => {
    const requestId = ++rowRequestId
    isLoadingRows.value = true

    try {
      const result = await agGridMockApi.queryInventory({
        page: page.value,
        pageSize: pageSizeNumber.value,
        quickSearch: quickSearch.value,
        sortModel: sortModel.value,
        filterModel: filterModel.value,
        dropdownFilters,
      })

      if (requestId !== rowRequestId) return

      rowData.value = result.rows
      total.value = result.total
      page.value = result.page
      loadedAt.value = new Date().toLocaleTimeString('zh-TW', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    } finally {
      if (requestId === rowRequestId) {
        isLoadingRows.value = false
      }
    }
  }

  const loadLookupOptions = async () => {
    isLoadingLookups.value = true

    try {
      lookupOptions.value = await agGridMockApi.getLookupOptions()
    } finally {
      isLoadingLookups.value = false
    }
  }

  const handleSortChanged = (event: SortChangedEvent<AgGridRowData>) => {
    sortModel.value = event.api
      .getColumnState()
      .filter((column) => column.sort === 'asc' || column.sort === 'desc')
      .map((column) => ({
        colId: column.colId,
        sort: column.sort as 'asc' | 'desc',
        sortIndex: column.sortIndex,
      }))

    page.value = 1
    void loadRows()
  }

  const handleFilterChanged = (event: FilterChangedEvent<AgGridRowData>) => {
    filterModel.value = event.api.getFilterModel() as InventoryFilterModel
    page.value = 1
    void loadRows()
  }

  const applySearch = () => {
    page.value = 1
    void loadRows()
  }

  const resetQuery = () => {
    quickSearch.value = ''
    dropdownFilters.category = 'all'
    dropdownFilters.supplier = 'all'
    dropdownFilters.status = 'all'
    dropdownFilters.warehouse = 'all'
    filterModel.value = {}
    sortModel.value = []
    page.value = 1

    const api = getGridApi()
    api?.setFilterModel(null)
    api?.applyColumnState({ defaultState: { sort: null } })
    void loadRows()
  }

  const goToPage = (nextPage: number) => {
    const clampedPage = Math.min(Math.max(nextPage, 1), totalPages.value)
    if (clampedPage === page.value) return

    page.value = clampedPage
    void loadRows()
  }

  watch(
    [
      () => dropdownFilters.category,
      () => dropdownFilters.supplier,
      () => dropdownFilters.status,
      () => dropdownFilters.warehouse,
      pageSize,
    ],
    () => {
      page.value = 1
      void loadRows()
    },
  )

  onMounted(async () => {
    await loadLookupOptions()
    await loadRows()
  })
</script>

<template>
  <div class="flex w-full flex-col gap-6">
    <div class="flex flex-col gap-4 px-1 lg:flex-row lg:items-end lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="rounded-lg border border-border bg-muted p-2 text-primary">
          <Database :size="22" />
        </div>
        <div class="flex flex-col gap-1">
          <div class="flex flex-wrap items-center gap-2">
            <h1 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              AG Grid API Demo
            </h1>
            <Badge variant="secondary">Mock API</Badge>
          </div>
          <p class="max-w-2xl text-sm text-muted-foreground">
            使用分頁查詢資料來源、遠端 lookup 下拉清單、欄位排序與欄位篩選。
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2 text-xs text-muted-foreground">
        <span>Rows {{ formatNumber(total) }}</span>
        <span class="h-1 w-1 rounded-full bg-muted-foreground/50"></span>
        <span>{{ loadedAt || '尚未查詢' }}</span>
      </div>
    </div>

    <Card>
      <CardHeader class="gap-1">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle>查詢條件</CardTitle>
            <CardDescription>外部條件與 AG Grid 欄位 filter 會一起送進 mock API。</CardDescription>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <Button variant="outline" size="sm" :disabled="isLoadingLookups" @click="loadLookupOptions">
              <RefreshCw :size="15" />
              重新載入下拉
            </Button>
            <Button variant="ghost" size="sm" :disabled="!hasActiveQuery" @click="resetQuery">
              <FilterX :size="15" />
              清除
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-[1.4fr_repeat(5,minmax(0,1fr))]">
          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">關鍵字</span>
            <div class="flex gap-2">
              <Input
                v-model="quickSearch"
                placeholder="料號、品名、供應商"
                @keydown.enter.prevent="applySearch"
              />
              <Button size="icon" :disabled="isLoadingRows" aria-label="查詢" @click="applySearch">
                <Search :size="16" />
              </Button>
            </div>
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">分類</span>
            <Select v-model="dropdownFilters.category" :disabled="isLoadingLookups">
              <SelectTrigger>
                <SelectValue placeholder="全部分類" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">全部分類</SelectItem>
                  <SelectItem v-for="category in lookupOptions.categories" :key="category" :value="category">
                    {{ category }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">供應商</span>
            <Select v-model="dropdownFilters.supplier" :disabled="isLoadingLookups">
              <SelectTrigger>
                <SelectValue placeholder="全部供應商" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">全部供應商</SelectItem>
                  <SelectItem v-for="supplier in lookupOptions.suppliers" :key="supplier" :value="supplier">
                    {{ supplier }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">狀態</span>
            <Select v-model="dropdownFilters.status" :disabled="isLoadingLookups">
              <SelectTrigger>
                <SelectValue placeholder="全部狀態" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">全部狀態</SelectItem>
                  <SelectItem v-for="status in lookupOptions.statuses" :key="status" :value="status">
                    {{ status }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">倉庫</span>
            <Select v-model="dropdownFilters.warehouse" :disabled="isLoadingLookups">
              <SelectTrigger>
                <SelectValue placeholder="全部倉庫" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">全部倉庫</SelectItem>
                  <SelectItem v-for="warehouse in lookupOptions.warehouses" :key="warehouse" :value="warehouse">
                    {{ warehouse }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-xs font-medium text-muted-foreground">每頁</span>
            <Select v-model="pageSize">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </label>
        </div>
      </CardContent>
    </Card>

    <Card class="overflow-hidden">
      <CardHeader class="border-b border-border/60 bg-muted/30">
        <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <CardTitle>庫存資料</CardTitle>
            <CardDescription>
              {{ pageStart }} - {{ pageEnd }} / {{ formatNumber(total) }}
            </CardDescription>
          </div>
          <Badge variant="outline">
            Page {{ page }} / {{ totalPages }}
          </Badge>
        </div>
      </CardHeader>
      <CardContent class="p-0">
        <div class="relative p-4">
          <AgGrid
            ref="gridRef"
            :row-data="rowData"
            :column-defs="columnDefs"
            :grid-options="gridOptions"
            height="560px"
          />

          <div
            v-if="isLoadingRows"
            class="absolute inset-4 grid place-items-center rounded-xl bg-background/70 backdrop-blur-sm"
          >
            <div class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 text-sm shadow-sm">
              <RefreshCw :size="16" class="animate-spin text-primary" />
              <span>查詢中</span>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3 border-t border-border/60 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-xs text-muted-foreground">
            Sort {{ sortModel.length }} · Filter {{ Object.keys(filterModel).length }}
          </p>
          <div class="flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" :disabled="page <= 1 || isLoadingRows" @click="goToPage(page - 1)">
              上一頁
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="page >= totalPages || isLoadingRows"
              @click="goToPage(page + 1)"
            >
              下一頁
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
