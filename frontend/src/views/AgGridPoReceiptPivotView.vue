<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue'
  import type { ICellRendererParams, SpanRowsParams, ValueFormatterParams } from 'ag-grid-community'
  import {
    AgGrid,
    type AgGridColumnDef,
    type AgGridOptions,
    type AgGridRowData,
  } from '@/components/ui/ag-grid'
  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import { Input } from '@/components/ui/input'
  import {
    poReceiptPivotMockApi,
    type PoReceiptGapStatus,
    type PoReceiptMatrixDataset,
    type PoReceiptMatrixRow,
  } from '@/services/poReceiptPivotMockApi'
  import { ChevronDown, FilterX, PackageSearch, RefreshCw } from 'lucide-vue-next'
  import { useI18n } from 'vue-i18n'

  const { locale, t } = useI18n()

  const dataset = ref<PoReceiptMatrixDataset | null>(null)
  const isLoading = ref(false)
  const quickSearch = ref('')
  const selectedSuppliers = ref<string[]>([])
  const selectedBuyers = ref<string[]>([])
  const selectedPlants = ref<string[]>([])
  const lineAccentPalette = ['#38bdf8', '#22c55e', '#f59e0b', '#a78bfa', '#ef4444', '#14b8a6']

  const localeTag = computed(() => (locale.value === 'zh-TW' ? 'zh-TW' : 'en-US'))
  const lookups = computed(() => dataset.value?.lookups)
  const loadedAtLabel = computed(() => {
    if (!dataset.value?.loadedAt) {
      return t('poReceiptPivotDemo.footer.notLoaded')
    }

    return new Intl.DateTimeFormat(localeTag.value, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(new Date(dataset.value.loadedAt))
  })

  const formatNumber = (value: unknown) => Number(value ?? 0).toLocaleString(localeTag.value)
  const formatGap = (value: unknown) => {
    const numericValue = Number(value ?? 0)
    return `${numericValue > 0 ? '+' : ''}${numericValue}d`
  }
  const getGapLabel = (status: PoReceiptGapStatus) =>
    t(`poReceiptPivotDemo.grid.gapStatuses.${status}`)
  const getGapClassName = (status: PoReceiptGapStatus) => {
    const classNameMap: Record<PoReceiptGapStatus, string> = {
      late: 'bg-rose-500/10 text-rose-700 dark:text-rose-300',
      risk: 'bg-amber-500/10 text-amber-700 dark:text-amber-300',
      onTrack: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
      ahead: 'bg-sky-500/10 text-sky-700 dark:text-sky-300',
    }

    return classNameMap[status]
  }

  const quantityFormatter = (params: ValueFormatterParams<AgGridRowData>) => {
    if (params.value === null || params.value === undefined || params.value === '') {
      return ''
    }

    return formatNumber(params.value)
  }

  const gapFormatter = (params: ValueFormatterParams<AgGridRowData>) => {
    if (params.value === null || params.value === undefined || params.value === '') {
      return ''
    }

    return formatGap(params.value)
  }

  type SearchFieldKey =
    | 'po'
    | 'line'
    | 'supplier'
    | 'buyer'
    | 'plant'
    | 'item'
    | 'schedule'
    | 'target'
    | 'range'
    | 'gap'

  const searchAliases: Record<string, SearchFieldKey> = {
    po: 'po',
    line: 'line',
    supplier: 'supplier',
    sup: 'supplier',
    buyer: 'buyer',
    plant: 'plant',
    item: 'item',
    part: 'item',
    schedule: 'schedule',
    sched: 'schedule',
    target: 'target',
    range: 'range',
    gap: 'gap',
  }

  const getLineAccentColor = (lineBandIndex: number) =>
    lineAccentPalette[lineBandIndex % lineAccentPalette.length]

  const buildSearchFields = (row: PoReceiptMatrixRow): Record<SearchFieldKey, string> => ({
    po: row.poNumber.toLowerCase(),
    line: `${row.poLineNumber} ${row.poLineLabel}`.toLowerCase(),
    supplier: row.supplierName.toLowerCase(),
    buyer: row.buyerName.toLowerCase(),
    plant: row.plantCode.toLowerCase(),
    item: `${row.itemCode} ${row.itemName}`.toLowerCase(),
    schedule: `${row.scheduleNo ?? ''} ${row.commitDate ?? ''}`.toLowerCase(),
    target:
      `${row.targetDate ?? ''} ${row.targetRangeLabel ?? ''} ${row.mappedRangeLabel ?? ''}`.toLowerCase(),
    range:
      `${row.targetRangeLabel ?? ''} ${row.mappedRangeLabel ?? ''} ${row.mappedQuantity ?? ''}`.toLowerCase(),
    gap: row.targetGapStatus
      ? `${row.targetGapStatus} ${getGapLabel(row.targetGapStatus)} ${row.targetGapDays ?? ''}`.toLowerCase()
      : `${row.targetGapDays ?? ''}`.toLowerCase(),
  })

  const matchesSearchToken = (row: PoReceiptMatrixRow, token: string) => {
    const searchFields = buildSearchFields(row)
    const separatorIndex = token.indexOf(':')

    if (separatorIndex > 0) {
      const alias = token.slice(0, separatorIndex)
      const fieldKey = searchAliases[alias]
      const searchTerm = token.slice(separatorIndex + 1)

      if (fieldKey && searchTerm) {
        return searchFields[fieldKey].includes(searchTerm)
      }
    }

    return Object.values(searchFields).some((value) => value.includes(token))
  }

  const filteredRows = computed(() => {
    const rows = dataset.value?.rows ?? []
    const tokens = quickSearch.value.trim().toLowerCase().split(/\s+/).filter(Boolean)

    return rows.filter((row) => {
      if (
        selectedSuppliers.value.length > 0 &&
        !selectedSuppliers.value.includes(row.supplierName)
      ) {
        return false
      }

      if (selectedBuyers.value.length > 0 && !selectedBuyers.value.includes(row.buyerName)) {
        return false
      }

      if (selectedPlants.value.length > 0 && !selectedPlants.value.includes(row.plantCode)) {
        return false
      }

      if (tokens.length === 0) return true

      return tokens.every((token) => matchesSearchToken(row, token))
    })
  })

  const totalRows = computed(() => filteredRows.value.length)
  const hasActiveFilters = computed(
    () =>
      Boolean(quickSearch.value.trim()) ||
      selectedSuppliers.value.length > 0 ||
      selectedBuyers.value.length > 0 ||
      selectedPlants.value.length > 0,
  )

  const spanWithinLine = (params: SpanRowsParams<AgGridRowData>) => {
    const rowA = params.nodeA?.data as PoReceiptMatrixRow | undefined
    const rowB = params.nodeB?.data as PoReceiptMatrixRow | undefined

    return Boolean(rowA && rowB && rowA.poLineId === rowB.poLineId)
  }

  const spanWithinSchedule = (params: SpanRowsParams<AgGridRowData>) => {
    const rowA = params.nodeA?.data as PoReceiptMatrixRow | undefined
    const rowB = params.nodeB?.data as PoReceiptMatrixRow | undefined

    return Boolean(
      rowA &&
      rowB &&
      rowA.poLineId === rowB.poLineId &&
      rowA.scheduleSpanKey &&
      rowA.scheduleSpanKey === rowB.scheduleSpanKey,
    )
  }

  const spanWithinTarget = (params: SpanRowsParams<AgGridRowData>) => {
    const rowA = params.nodeA?.data as PoReceiptMatrixRow | undefined
    const rowB = params.nodeB?.data as PoReceiptMatrixRow | undefined

    return Boolean(
      rowA &&
      rowB &&
      rowA.poLineId === rowB.poLineId &&
      rowA.targetSpanKey &&
      rowA.targetSpanKey === rowB.targetSpanKey,
    )
  }

  const isSelected = (selectedValues: string[], value: string) => selectedValues.includes(value)

  const updateMultiSelection = (
    model: { value: string[] },
    value: string,
    checked: boolean | 'indeterminate',
  ) => {
    const nextValues = new Set(model.value)

    if (checked === true) {
      nextValues.add(value)
    } else {
      nextValues.delete(value)
    }

    model.value = Array.from(nextValues)
  }

  const clearMultiSelection = (model: { value: string[] }) => {
    model.value = []
  }

  const clearSupplierSelection = () => clearMultiSelection(selectedSuppliers)
  const clearBuyerSelection = () => clearMultiSelection(selectedBuyers)
  const clearPlantSelection = () => clearMultiSelection(selectedPlants)

  const toggleSupplierSelection = (value: string, checked: boolean | 'indeterminate') => {
    updateMultiSelection(selectedSuppliers, value, checked)
  }

  const toggleBuyerSelection = (value: string, checked: boolean | 'indeterminate') => {
    updateMultiSelection(selectedBuyers, value, checked)
  }

  const togglePlantSelection = (value: string, checked: boolean | 'indeterminate') => {
    updateMultiSelection(selectedPlants, value, checked)
  }

  const renderPoGroupLabel = (params: ICellRendererParams<AgGridRowData>) => {
    const poNumber = String(params.value ?? '')
    const lineMap = new Map<string, PoReceiptMatrixRow>()

    for (const rowNode of params.node.allLeafChildren ?? []) {
      const row = rowNode.data as PoReceiptMatrixRow | undefined
      if (row && !lineMap.has(row.poLineId)) {
        lineMap.set(row.poLineId, row)
      }
    }

    const lineRows = Array.from(lineMap.values())
    const totalOrdered = lineRows.reduce((sum, row) => sum + row.lineOrderedQuantity, 0)
    const totalReceived = lineRows.reduce((sum, row) => sum + row.lineReceiptQuantity, 0)
    const receivedRate = totalOrdered > 0 ? Math.round((totalReceived / totalOrdered) * 100) : 0

    return `<div class="flex w-full items-center justify-between gap-4 py-2 pr-3"><div class="flex items-center gap-3"><span class="font-mono text-sm font-semibold">${poNumber}</span><span class="rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-xs text-primary">${formatNumber(lineRows.length)} ${t('poReceiptPivotDemo.grid.lineCountUnit')}</span></div><div class="hidden min-w-0 items-center gap-3 md:flex"><div class="h-2 w-32 overflow-hidden rounded-full" style="background:rgba(148,163,184,0.18)"><div class="h-full rounded-full" style="width:${Math.max(receivedRate, 4)}%;background:linear-gradient(90deg,#38bdf8 0%,#22c55e 100%)"></div></div><span class="whitespace-nowrap text-xs text-muted-foreground">${formatNumber(totalReceived)} / ${formatNumber(totalOrdered)}</span></div></div>`
  }

  const readonlyColumnProps = {
    editable: false,
    sortable: false,
    filter: false,
    suppressMovable: true,
  }

  const lineColumnProps = {
    ...readonlyColumnProps,
    spanRows: spanWithinLine,
  }

  const scheduleColumnProps = {
    ...readonlyColumnProps,
    spanRows: spanWithinSchedule,
  }

  const targetColumnProps = {
    ...readonlyColumnProps,
    spanRows: spanWithinTarget,
  }

  const columnDefs = computed<AgGridColumnDef[]>(() => [
    {
      ...readonlyColumnProps,
      field: 'poNumber',
      rowGroup: true,
      hide: true,
    },
    {
      headerName: t('poReceiptPivotDemo.grid.sections.line'),
      marryChildren: true,
      children: [
        {
          ...lineColumnProps,
          field: 'poLineLabel',
          headerName: t('poReceiptPivotDemo.grid.poLine'),
          minWidth: 180,
          cellClass: 'bg-muted/20',
          cellRenderer: (params: { data?: PoReceiptMatrixRow | null }) => {
            const row = params.data

            if (!row) return ''

            const accentColor = getLineAccentColor(row.lineBandIndex)
            const receivedRate = Math.round(row.lineReceiptRate * 100)

            return `<div class="flex flex-col gap-1.5 py-1"><div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full" style="background:${accentColor}"></span><span class="font-semibold">${t('poDetail.linePrefix')} ${row.poLineNumber}</span></div><span class="text-[11px] text-muted-foreground">${formatNumber(row.scheduleCount)} ${t('poReceiptPivotDemo.grid.scheduleSplitUnit')} / ${formatNumber(row.targetCount)} ${t('poReceiptPivotDemo.grid.targetSplitUnit')}</span><div class="flex items-center gap-2"><div class="h-1.5 w-24 overflow-hidden rounded-full" style="background:rgba(148,163,184,0.18)"><div class="h-full rounded-full" style="width:${Math.max(receivedRate, 4)}%;background:${accentColor}"></div></div><span class="text-[11px] text-muted-foreground">${receivedRate}% RT</span></div></div>`
          },
        },
        {
          ...lineColumnProps,
          field: 'supplierName',
          headerName: t('poReceiptPivotDemo.grid.supplier'),
          minWidth: 180,
          cellClass: 'bg-muted/20',
        },
        {
          ...lineColumnProps,
          field: 'buyerName',
          headerName: t('poReceiptPivotDemo.grid.buyer'),
          minWidth: 140,
          cellClass: 'bg-muted/20',
        },
        {
          ...lineColumnProps,
          field: 'plantCode',
          headerName: t('poReceiptPivotDemo.grid.plant'),
          width: 120,
          cellClass: 'bg-muted/20 font-mono text-xs',
        },
        {
          ...lineColumnProps,
          field: 'itemName',
          headerName: t('poReceiptPivotDemo.grid.item'),
          minWidth: 220,
          cellClass: 'bg-muted/20',
          cellRenderer: (params: { data?: PoReceiptMatrixRow | null }) => {
            const row = params.data

            if (!row) return ''

            return `<div class="flex flex-col gap-1 py-1"><span class="font-mono text-[11px] text-muted-foreground">${row.itemCode}</span><span>${row.itemName}</span></div>`
          },
        },
        {
          ...lineColumnProps,
          field: 'lineOrderedQuantity',
          headerName: t('poReceiptPivotDemo.grid.lineOrderedQty'),
          width: 130,
          valueFormatter: quantityFormatter,
          cellClass: 'bg-muted/20 font-mono text-right',
        },
        {
          ...lineColumnProps,
          field: 'lineReceiptQuantity',
          headerName: t('poReceiptPivotDemo.grid.lineRtQty'),
          width: 130,
          valueFormatter: quantityFormatter,
          cellClass: 'bg-muted/20 font-mono text-right text-emerald-700 dark:text-emerald-300',
        },
        {
          ...lineColumnProps,
          field: 'lineOpenQuantity',
          headerName: t('poReceiptPivotDemo.grid.lineOpenQty'),
          width: 130,
          valueFormatter: quantityFormatter,
          cellClass: 'bg-muted/20 font-mono text-right',
        },
      ],
    },
    {
      headerName: t('poReceiptPivotDemo.grid.sections.schedule'),
      marryChildren: true,
      children: [
        {
          ...scheduleColumnProps,
          field: 'scheduleNo',
          headerName: t('poReceiptPivotDemo.grid.scheduleNo'),
          width: 100,
          cellClass: 'font-mono text-xs',
        },
        {
          ...scheduleColumnProps,
          field: 'commitDate',
          headerName: t('poReceiptPivotDemo.grid.commitDate'),
          width: 126,
          cellClass: 'font-mono text-xs',
        },
        {
          ...scheduleColumnProps,
          field: 'scheduleQuantity',
          headerName: t('poReceiptPivotDemo.grid.scheduleQty'),
          width: 126,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right',
        },
        {
          ...scheduleColumnProps,
          field: 'scheduleOpenQuantity',
          headerName: t('poReceiptPivotDemo.grid.scheduleOpenQty'),
          width: 120,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right',
        },
        {
          ...scheduleColumnProps,
          field: 'scheduleReceiptQuantity',
          headerName: t('poReceiptPivotDemo.grid.scheduleRtQty'),
          width: 120,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right text-emerald-700 dark:text-emerald-300',
        },
        {
          ...scheduleColumnProps,
          field: 'scheduleBalanceQuantity',
          headerName: t('poReceiptPivotDemo.grid.scheduleBalanceQty'),
          width: 120,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right text-amber-700 dark:text-amber-300',
        },
      ],
    },
    {
      headerName: t('poReceiptPivotDemo.grid.sections.target'),
      marryChildren: true,
      children: [
        {
          ...targetColumnProps,
          field: 'targetDate',
          headerName: t('poReceiptPivotDemo.grid.targetDate'),
          width: 126,
          cellClass: 'font-mono text-xs',
        },
        {
          ...targetColumnProps,
          field: 'targetQuantity',
          headerName: t('poReceiptPivotDemo.grid.targetQty'),
          width: 120,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right',
        },
        {
          ...targetColumnProps,
          field: 'targetRangeLabel',
          headerName: t('poReceiptPivotDemo.grid.targetRange'),
          minWidth: 150,
          cellClass: 'font-mono text-xs',
        },
        {
          ...readonlyColumnProps,
          field: 'mappedQuantity',
          headerName: t('poReceiptPivotDemo.grid.mappedQty'),
          width: 120,
          valueFormatter: quantityFormatter,
          cellClass: 'font-mono text-right text-sky-600 dark:text-sky-300',
        },
        {
          ...readonlyColumnProps,
          field: 'mappedRangeLabel',
          headerName: t('poReceiptPivotDemo.grid.mappedRange'),
          minWidth: 150,
          cellClass: 'font-mono text-xs',
        },
        {
          ...targetColumnProps,
          field: 'targetGapDays',
          headerName: t('poReceiptPivotDemo.grid.targetGapDays'),
          width: 110,
          valueFormatter: gapFormatter,
          cellClassRules: {
            'font-mono text-right text-rose-600 dark:text-rose-300': (params) =>
              Number(params.value ?? 0) > 0,
            'font-mono text-right text-sky-600 dark:text-sky-300': (params) =>
              Number(params.value ?? 0) < 0,
            'font-mono text-right text-emerald-600 dark:text-emerald-300': (params) =>
              Number(params.value ?? 0) === 0,
          },
        },
        {
          ...targetColumnProps,
          field: 'targetGapStatus',
          headerName: t('poReceiptPivotDemo.grid.targetGapStatus'),
          width: 130,
          cellRenderer: (params: { value: PoReceiptGapStatus | null }) => {
            const status = params.value

            if (!status) return ''

            return `<span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${getGapClassName(status)}">${getGapLabel(status)}</span>`
          },
        },
      ],
    },
  ])

  const gridOptions = computed<AgGridOptions>(() => ({
    enableCellSpan: true,
    animateRows: false,
    rowHeight: 56,
    headerHeight: 42,
    groupHeaderHeight: 40,
    groupDisplayType: 'groupRows',
    groupDefaultExpanded: 1,
    suppressGroupRowsSticky: true,
    groupRowRendererParams: {
      suppressCount: true,
      innerRenderer: renderPoGroupLabel,
    },
    getRowHeight: (params) => (params.node.group ? 48 : 56),
    rowClassRules: {
      'po-line-start-row': (params) =>
        Boolean((params.data as PoReceiptMatrixRow | undefined)?.isLineStart),
      'po-line-band-row': (params) =>
        ((params.data as PoReceiptMatrixRow | undefined)?.lineBandIndex ?? 0) % 2 === 1,
    },
    getRowId: (params) => String((params.data as PoReceiptMatrixRow | undefined)?.id ?? ''),
  }))

  const loadDataset = async () => {
    isLoading.value = true

    try {
      dataset.value = await poReceiptPivotMockApi.getDataset()
    } finally {
      isLoading.value = false
    }
  }

  const resetFilters = () => {
    quickSearch.value = ''
    selectedSuppliers.value = []
    selectedBuyers.value = []
    selectedPlants.value = []
  }

  onMounted(() => {
    void loadDataset()
  })
</script>

<template>
  <div class="flex w-full flex-col gap-5 animate-in fade-in slide-in-from-bottom-3 duration-500">
    <div class="flex flex-col gap-4 px-1 xl:flex-row xl:items-end xl:justify-between">
      <div class="flex items-start gap-3">
        <div class="rounded-2xl border border-primary/20 bg-primary/10 p-3 text-primary shadow-sm">
          <PackageSearch :size="24" />
        </div>
        <div class="space-y-2">
          <h1 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            {{ t('poReceiptPivotDemo.title') }}
          </h1>
          <p class="max-w-3xl text-sm text-muted-foreground">
            {{ t('poReceiptPivotDemo.subtitle') }}
          </p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground xl:justify-end">
        <span>{{ formatNumber(totalRows) }} {{ t('poReceiptPivotDemo.footer.totalRows') }}</span>
        <span class="h-1 w-1 rounded-full bg-muted-foreground/50"></span>
        <span>{{ t('poReceiptPivotDemo.footer.loadedAt') }} {{ loadedAtLabel }}</span>
      </div>
    </div>

    <Card>
      <CardContent class="flex flex-col gap-3 p-4">
        <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex flex-1 flex-wrap items-center gap-2">
            <div class="w-full sm:w-[280px] xl:w-[320px]">
              <Input
                v-model="quickSearch"
                :placeholder="t('poReceiptPivotDemo.filters.searchPlaceholder')"
                :aria-label="t('poReceiptPivotDemo.filters.searchLabel')"
              />
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                  variant="outline"
                  class="h-9 gap-2 rounded-lg"
                  :class="
                    selectedSuppliers.length > 0
                      ? 'border-primary/40 bg-primary/5'
                      : 'border-border/60 bg-background'
                  "
                >
                  <span class="text-muted-foreground">{{
                    t('poReceiptPivotDemo.filters.supplierLabel')
                  }}</span>
                  <Badge v-if="selectedSuppliers.length > 0" variant="secondary">
                    {{ formatNumber(selectedSuppliers.length) }}
                  </Badge>
                  <span v-if="selectedSuppliers.length > 0" class="text-xs">
                    {{ t('poReceiptPivotDemo.filters.selected') }}
                  </span>
                  <ChevronDown :size="14" class="text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent class="w-60">
                <DropdownMenuLabel>{{
                  t('poReceiptPivotDemo.filters.supplierLabel')
                }}</DropdownMenuLabel>
                <DropdownMenuItem
                  :disabled="selectedSuppliers.length === 0"
                  class="justify-between text-muted-foreground"
                  @select.prevent="clearSupplierSelection"
                >
                  {{ t('poReceiptPivotDemo.filters.clearSelection') }}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  v-for="supplier in lookups?.suppliers ?? []"
                  :key="supplier"
                  :checked="isSelected(selectedSuppliers, supplier)"
                  @select.prevent
                  @update:checked="toggleSupplierSelection(supplier, $event)"
                >
                  {{ supplier }}
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                  variant="outline"
                  class="h-9 gap-2 rounded-lg"
                  :class="
                    selectedBuyers.length > 0
                      ? 'border-primary/40 bg-primary/5'
                      : 'border-border/60 bg-background'
                  "
                >
                  <span class="text-muted-foreground">{{
                    t('poReceiptPivotDemo.filters.buyerLabel')
                  }}</span>
                  <Badge v-if="selectedBuyers.length > 0" variant="secondary">
                    {{ formatNumber(selectedBuyers.length) }}
                  </Badge>
                  <span v-if="selectedBuyers.length > 0" class="text-xs">
                    {{ t('poReceiptPivotDemo.filters.selected') }}
                  </span>
                  <ChevronDown :size="14" class="text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent class="w-56">
                <DropdownMenuLabel>{{
                  t('poReceiptPivotDemo.filters.buyerLabel')
                }}</DropdownMenuLabel>
                <DropdownMenuItem
                  :disabled="selectedBuyers.length === 0"
                  class="justify-between text-muted-foreground"
                  @select.prevent="clearBuyerSelection"
                >
                  {{ t('poReceiptPivotDemo.filters.clearSelection') }}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  v-for="buyer in lookups?.buyers ?? []"
                  :key="buyer"
                  :checked="isSelected(selectedBuyers, buyer)"
                  @select.prevent
                  @update:checked="toggleBuyerSelection(buyer, $event)"
                >
                  {{ buyer }}
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                  variant="outline"
                  class="h-9 gap-2 rounded-lg"
                  :class="
                    selectedPlants.length > 0
                      ? 'border-primary/40 bg-primary/5'
                      : 'border-border/60 bg-background'
                  "
                >
                  <span class="text-muted-foreground">{{
                    t('poReceiptPivotDemo.filters.plantLabel')
                  }}</span>
                  <Badge v-if="selectedPlants.length > 0" variant="secondary">
                    {{ formatNumber(selectedPlants.length) }}
                  </Badge>
                  <span v-if="selectedPlants.length > 0" class="text-xs">
                    {{ t('poReceiptPivotDemo.filters.selected') }}
                  </span>
                  <ChevronDown :size="14" class="text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent class="w-48">
                <DropdownMenuLabel>{{
                  t('poReceiptPivotDemo.filters.plantLabel')
                }}</DropdownMenuLabel>
                <DropdownMenuItem
                  :disabled="selectedPlants.length === 0"
                  class="justify-between text-muted-foreground"
                  @select.prevent="clearPlantSelection"
                >
                  {{ t('poReceiptPivotDemo.filters.clearSelection') }}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  v-for="plant in lookups?.plants ?? []"
                  :key="plant"
                  :checked="isSelected(selectedPlants, plant)"
                  @select.prevent
                  @update:checked="togglePlantSelection(plant, $event)"
                >
                  {{ plant }}
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" :disabled="isLoading" @click="loadDataset">
              <RefreshCw :size="15" :class="isLoading ? 'animate-spin' : ''" />
              {{ t('poReceiptPivotDemo.filters.refresh') }}
            </Button>
            <Button variant="ghost" size="sm" :disabled="!hasActiveFilters" @click="resetFilters">
              <FilterX :size="15" />
              {{ t('poReceiptPivotDemo.filters.reset') }}
            </Button>
          </div>
        </div>

        <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2">
          <Badge
            v-if="quickSearch.trim()"
            variant="outline"
            class="border-primary/30 bg-primary/5 text-foreground"
          >
            {{ t('poReceiptPivotDemo.filters.searchLabel') }}: {{ quickSearch }}
          </Badge>
          <Badge
            v-for="supplier in selectedSuppliers"
            :key="`supplier-${supplier}`"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ t('poReceiptPivotDemo.filters.supplierLabel') }}: {{ supplier }}
          </Badge>
          <Badge
            v-for="buyer in selectedBuyers"
            :key="`buyer-${buyer}`"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ t('poReceiptPivotDemo.filters.buyerLabel') }}: {{ buyer }}
          </Badge>
          <Badge
            v-for="plant in selectedPlants"
            :key="`plant-${plant}`"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ t('poReceiptPivotDemo.filters.plantLabel') }}: {{ plant }}
          </Badge>
        </div>

        <p class="text-xs text-muted-foreground">
          {{ t('poReceiptPivotDemo.filters.searchHint') }}
        </p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader class="gap-1 pb-3">
        <CardTitle>{{ t('poReceiptPivotDemo.grid.title') }}</CardTitle>
        <CardDescription>{{ t('poReceiptPivotDemo.grid.description') }}</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          v-if="isLoading"
          class="flex min-h-[560px] items-center justify-center gap-3 rounded-xl border border-dashed border-border/60 bg-muted/15 text-sm text-muted-foreground"
        >
          <RefreshCw :size="16" class="animate-spin" />
          <span>{{ t('header.loading') }}</span>
        </div>
        <div
          v-else-if="filteredRows.length === 0"
          class="flex min-h-[560px] items-center justify-center rounded-xl border border-dashed border-border/60 bg-muted/15 text-sm text-muted-foreground"
        >
          {{ t('poReceiptPivotDemo.grid.empty') }}
        </div>
        <AgGrid
          v-else
          :row-data="filteredRows"
          :column-defs="columnDefs"
          :grid-options="gridOptions"
          height="720px"
        />
      </CardContent>
    </Card>
  </div>
</template>

<style scoped>
  :deep(.po-line-start-row .ag-cell) {
    border-top: 1px solid rgba(56, 189, 248, 0.22);
  }

  :deep(.po-line-band-row .ag-cell) {
    background-color: rgba(148, 163, 184, 0.03);
  }

  :deep(.ag-full-width-row .ag-cell-wrapper) {
    width: 100%;
  }
</style>
