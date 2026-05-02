<script setup lang="ts">
  import { computed, ref, watch } from 'vue'
  import type { CheckboxCheckedState } from 'reka-ui'
  import { useI18n } from 'vue-i18n'
  import { toast } from 'vue-sonner'

  import { usePoManagement } from '@/composables/usePoManagement'
  import { cn } from '@/lib/utils'
  import type {
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderPullInRecord,
    PurchaseOrderReceipt,
    PurchaseOrderSchedule,
  } from '@/services/api'
  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import { Checkbox } from '@/components/ui/checkbox'
  import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogTitle,
  } from '@/components/ui/dialog'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'
  import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from '@/components/ui/select'
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from '@/components/ui/table'
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
  import { Textarea } from '@/components/ui/textarea'
  import {
    AlertCircle,
    ArrowUpDown,
    Boxes,
    CalendarRange,
    ChevronDown,
    ChevronRight,
    Filter,
    FolderTree,
    History,
    PackageSearch,
    PencilLine,
    ReceiptText,
    RotateCcw,
    Search,
    TrendingUpDown,
    Truck,
    ListTree,
    Mail,
    CalendarClock,
    Download,
    XCircle,
  } from 'lucide-vue-next'

  type ReceiptRow = Readonly<PurchaseOrderReceipt>
  type PullInRow = Readonly<PurchaseOrderPullInRecord>
  type StatusKey =
    | 'completed'
    | 'partial'
    | 'delayed'
    | 'inTransit'
    | 'newArrival'
    | 'pullInPlanned'
  type GroupBy = 'order' | 'supplier' | 'status' | 'none'
  type SortBy = 'nextCommitAsc' | 'nextCommitDesc' | 'supplierAsc' | 'openDesc' | 'pullInDesc'
  type CheckedState = CheckboxCheckedState

  interface ScheduleRow extends Omit<PurchaseOrderSchedule, 'receipts'> {
    readonly receipts: readonly ReceiptRow[]
  }

  interface LineRow extends Omit<PurchaseOrderLine, 'schedules' | 'pull_in_records'> {
    readonly schedules: readonly ScheduleRow[]
    readonly pull_in_records: readonly PullInRow[]
  }

  interface OrderRow extends Omit<PurchaseOrder, 'lines'> {
    readonly lines: readonly LineRow[]
  }

  interface ReceiptDetail extends ReceiptRow {
    readonly schedule_no: string
  }

  interface ScheduleContext {
    readonly order: OrderRow
    readonly line: LineRow
    readonly schedule: ScheduleRow
  }

  interface LineEntry {
    readonly order: OrderRow
    readonly line: LineRow
    readonly status: StatusKey
    readonly nextCommitDate: string
    readonly openQuantity: number
    readonly receivedQuantity: number
    readonly pullInQuantity: number
    readonly receiptCount: number
  }

  interface LineGroup {
    readonly key: string
    readonly label: string
    readonly badge: string
    readonly description: string
    readonly entries: readonly LineEntry[]
  }

  const statusKeys: readonly StatusKey[] = [
    'completed',
    'partial',
    'delayed',
    'inTransit',
    'newArrival',
    'pullInPlanned',
  ]

  const sortOptions: readonly { value: SortBy; labelKey: string }[] = [
    { value: 'nextCommitAsc', labelKey: 'poManagement.controls.sortCommitAsc' },
    { value: 'nextCommitDesc', labelKey: 'poManagement.controls.sortCommitDesc' },
    { value: 'supplierAsc', labelKey: 'poManagement.controls.sortSupplierAsc' },
    { value: 'openDesc', labelKey: 'poManagement.controls.sortOpenDesc' },
    { value: 'pullInDesc', labelKey: 'poManagement.controls.sortPullInDesc' },
  ]

  const groupOptions: readonly { value: GroupBy; labelKey: string }[] = [
    { value: 'order', labelKey: 'poManagement.controls.groupOrder' },
    { value: 'supplier', labelKey: 'poManagement.controls.groupSupplier' },
    { value: 'status', labelKey: 'poManagement.controls.groupStatus' },
    { value: 'none', labelKey: 'poManagement.controls.groupNone' },
  ]

  const stickyHeaderCheckboxClass =
    'w-12 xl:w-14 sticky left-0 z-30 bg-background shadow-[inset_-1px_0_0_hsl(var(--border))]'
  const stickyHeaderPrimaryClass =
    'min-w-[12rem] md:min-w-[14rem] xl:min-w-[18rem] sticky left-12 xl:left-14 z-30 bg-background shadow-[inset_-1px_0_0_hsl(var(--border))]'
  const stickyGroupCheckboxClass =
    'w-12 xl:w-14 align-top bg-muted/20 sticky left-0 z-20 xl:bg-muted/20 shadow-[inset_-1px_0_0_hsl(var(--border))]'
  const stickyGroupPrimaryClass =
    'min-w-[12rem] md:min-w-[14rem] xl:min-w-[18rem] align-top bg-muted/20 sticky left-12 xl:left-14 z-20 xl:bg-muted/20 shadow-[inset_-1px_0_0_hsl(var(--border))]'
  const stickyLineCheckboxClass =
    'w-12 xl:w-14 align-top bg-background group-hover:bg-accent/20 sticky left-0 z-10 xl:bg-background shadow-[inset_-1px_0_0_hsl(var(--border))] xl:group-hover:bg-accent/20'
  const stickyLinePrimaryClass =
    'min-w-[12rem] md:min-w-[14rem] xl:min-w-[18rem] align-top bg-background group-hover:bg-accent/20 sticky left-12 xl:left-14 z-10 xl:bg-background shadow-[inset_-1px_0_0_hsl(var(--border))] xl:group-hover:bg-accent/20'

  const { t } = useI18n()
  const { orders, isLoading, error, applyPullIn, updateSchedule, resetDemoData } = usePoManagement()

  const activeTab = ref('list')
  const searchQuery = ref('')
  const statusFilter = ref<'all' | StatusKey>('all')
  const supplierFilter = ref('all')
  const sortBy = ref<SortBy>('nextCommitAsc')
  const groupBy = ref<GroupBy>('order')
  const expandedGroupKeys = ref<string[]>([])
  const expandedLineIds = ref<string[]>([])
  const selectedLineIds = ref<string[]>([])
  const isPullInDialogOpen = ref(false)
  const isScheduleDialogOpen = ref(false)
  const activePullInContext = ref<ScheduleContext | null>(null)
  const activeScheduleContext = ref<ScheduleContext | null>(null)
  const pullInForm = ref({
    target_date: '',
    quantity: '',
    note: '',
    requested_by: 'Planner Team',
  })
  const scheduleForm = ref({
    commit_date: '',
    quantity: '',
  })

  const supplierOptions = computed(() =>
    Array.from(
      new Set(orders.value.flatMap((order) => order.lines.map((line) => line.supplier_name))),
    ).sort((left, right) => left.localeCompare(right)),
  )

  const lineEntries = computed(() =>
    orders.value.flatMap((order) => order.lines.map((line) => buildLineEntry(order, line))),
  )

  const filteredLineEntries = computed(() => {
    const keyword = searchQuery.value.trim().toLowerCase()

    return lineEntries.value.filter((entry) => {
      const matchesSearch =
        keyword.length === 0 ||
        [
          entry.order.order_number,
          entry.order.notes,
          entry.line.line_number,
          entry.line.item_code,
          entry.line.item_name,
          entry.line.supplier_name,
          entry.line.notes,
        ]
          .join(' ')
          .toLowerCase()
          .includes(keyword)

      const matchesStatus = statusFilter.value === 'all' || entry.status === statusFilter.value
      const matchesSupplier =
        supplierFilter.value === 'all' || entry.line.supplier_name === supplierFilter.value

      return matchesSearch && matchesStatus && matchesSupplier
    })
  })

  const visibleGroups = computed<readonly LineGroup[]>(() => {
    const groupedEntries = new Map<string, LineEntry[]>()

    for (const entry of sortLineEntries(filteredLineEntries.value)) {
      const key =
        groupBy.value === 'none'
          ? 'all'
          : groupBy.value === 'order'
            ? entry.order.id
            : groupBy.value === 'supplier'
              ? entry.line.supplier_name
              : entry.status

      const bucket = groupedEntries.get(key) ?? []
      bucket.push(entry)
      groupedEntries.set(key, bucket)
    }

    return Array.from(groupedEntries.entries()).map(([key, entries]) => {
      const totalOpenQuantity = entries.reduce((total, entry) => total + entry.openQuantity, 0)

      if (groupBy.value === 'none') {
        return {
          key,
          label: t('poManagement.table.allLines'),
          badge: `${entries.length} ${t('poManagement.table.lineCount')}`,
          description: `${formatNumber(totalOpenQuantity)} ${t('poManagement.table.open')}`,
          entries,
        }
      }

      if (groupBy.value === 'order') {
        const order = entries[0].order
        return {
          key,
          label: order.order_number,
          badge: `${entries.length} ${t('poManagement.table.lineCount')}`,
          description: [
            order.buyer_name,
            `${formatNumber(totalOpenQuantity)} ${t('poManagement.table.open')}`,
            order.notes,
          ]
            .filter(Boolean)
            .join(' · '),
          entries,
        }
      }

      if (groupBy.value === 'supplier') {
        const distinctOrderCount = new Set(entries.map((entry) => entry.order.order_number)).size

        return {
          key,
          label: entries[0].line.supplier_name,
          badge: `${distinctOrderCount} PO`,
          description: `${entries.length} ${t('poManagement.table.lineCount')} · ${formatNumber(totalOpenQuantity)} ${t('poManagement.table.open')}`,
          entries,
        }
      }

      return {
        key,
        label: t(`poManagement.status.${entries[0].status}`),
        badge: `${entries.length} ${t('poManagement.table.lineCount')}`,
        description: `${formatNumber(totalOpenQuantity)} ${t('poManagement.table.open')}`,
        entries,
      }
    })
  })

  const orderCount = computed(
    () => new Set(filteredLineEntries.value.map((entry) => entry.order.id)).size,
  )
  const lineCount = computed(() => filteredLineEntries.value.length)
  const totalOpenQuantity = computed(() =>
    filteredLineEntries.value.reduce((total, entry) => total + entry.openQuantity, 0),
  )
  const totalPullInQuantity = computed(() =>
    filteredLineEntries.value.reduce((total, entry) => total + entry.pullInQuantity, 0),
  )
  const hasActiveFilters = computed(
    () =>
      searchQuery.value.trim().length > 0 ||
      statusFilter.value !== 'all' ||
      supplierFilter.value !== 'all' ||
      sortBy.value !== 'nextCommitAsc' ||
      groupBy.value !== 'order',
  )

  watch(
    filteredLineEntries,
    (entries) => {
      const visibleLineIds = new Set(entries.map((entry) => entry.line.id))

      expandedLineIds.value = expandedLineIds.value.filter((lineId) => visibleLineIds.has(lineId))
      selectedLineIds.value = selectedLineIds.value.filter((lineId) => visibleLineIds.has(lineId))

      if (entries.length > 0 && expandedLineIds.value.length === 0) {
        expandedLineIds.value = [entries[0].line.id]
      }
    },
    { immediate: true },
  )

  watch(
    visibleGroups,
    (groups) => {
      const visibleKeys = new Set(groups.map((group) => group.key))

      expandedGroupKeys.value = expandedGroupKeys.value.filter((groupKey) =>
        visibleKeys.has(groupKey),
      )

      if (groupBy.value === 'none') {
        expandedGroupKeys.value = ['all']
      } else if (groups.length > 0 && expandedGroupKeys.value.length === 0) {
        expandedGroupKeys.value = groups
          .slice(0, Math.min(groups.length, 2))
          .map((group) => group.key)
      }
    },
    { immediate: true },
  )

  function formatNumber(value: number) {
    return new Intl.NumberFormat('en-US').format(value)
  }

  function getScheduleOpenQuantity(schedule: ScheduleRow) {
    return Math.max(schedule.quantity - schedule.received_quantity, 0)
  }

  function getLineOpenQuantity(line: LineRow) {
    return line.schedules.reduce((total, schedule) => total + getScheduleOpenQuantity(schedule), 0)
  }

  function getLineReceivedQuantity(line: LineRow) {
    return line.schedules.reduce((total, schedule) => total + schedule.received_quantity, 0)
  }

  function getLinePullInQuantity(line: LineRow) {
    return line.pull_in_records.reduce((total, record) => total + record.quantity, 0)
  }

  function getLineNextCommitDate(line: LineRow) {
    const nextSchedule = [...line.schedules]
      .filter((schedule) => getScheduleOpenQuantity(schedule) > 0)
      .sort((left, right) => left.commit_date.localeCompare(right.commit_date))[0]

    return nextSchedule?.commit_date ?? line.schedules[0]?.commit_date ?? '—'
  }

  function getLineReceipts(line: LineRow): ReceiptDetail[] {
    return line.schedules.flatMap((schedule) =>
      schedule.receipts.map((receipt) => ({
        ...receipt,
        schedule_no: schedule.schedule_no,
      })),
    )
  }

  function getLineStatus(line: LineRow): StatusKey {
    const openQuantity = getLineOpenQuantity(line)
    const receivedQuantity = getLineReceivedQuantity(line)
    const pullInQuantity = getLinePullInQuantity(line)
    const nextCommitDate = getLineNextCommitDate(line)
    const today = new Date().toISOString().slice(0, 10)

    if (openQuantity === 0) return 'completed'
    if (nextCommitDate < today) return 'delayed'
    if (pullInQuantity > 0) return 'pullInPlanned'
    if (receivedQuantity > 0) return 'partial'
    if (nextCommitDate <= '2026-04-30') return 'inTransit'
    return 'newArrival'
  }

  function buildLineEntry(order: OrderRow, line: LineRow): LineEntry {
    return {
      order,
      line,
      status: getLineStatus(line),
      nextCommitDate: getLineNextCommitDate(line),
      openQuantity: getLineOpenQuantity(line),
      receivedQuantity: getLineReceivedQuantity(line),
      pullInQuantity: getLinePullInQuantity(line),
      receiptCount: getLineReceipts(line).length,
    }
  }

  function sortLineEntries(entries: readonly LineEntry[]) {
    return [...entries].sort((left, right) => {
      if (sortBy.value === 'nextCommitAsc') {
        return left.nextCommitDate.localeCompare(right.nextCommitDate)
      }

      if (sortBy.value === 'nextCommitDesc') {
        return right.nextCommitDate.localeCompare(left.nextCommitDate)
      }

      if (sortBy.value === 'supplierAsc') {
        return left.line.supplier_name.localeCompare(right.line.supplier_name)
      }

      if (sortBy.value === 'openDesc') {
        return right.openQuantity - left.openQuantity
      }

      return right.pullInQuantity - left.pullInQuantity
    })
  }

  function getStatusClasses(status: StatusKey) {
    const classes: Record<StatusKey, string> = {
      completed: 'border-emerald-500/30 bg-emerald-500/15 text-emerald-300',
      partial: 'border-amber-500/30 bg-amber-500/15 text-amber-300',
      delayed: 'border-rose-500/30 bg-rose-500/15 text-rose-300',
      inTransit: 'border-blue-500/30 bg-blue-500/15 text-blue-300',
      newArrival: 'border-cyan-500/30 bg-cyan-500/15 text-cyan-300',
      pullInPlanned: 'border-violet-500/30 bg-violet-500/15 text-violet-300',
    }

    return classes[status]
  }

  function getSupplierClasses(name: string) {
    if (name.includes('Foxconn')) return 'border-orange-500/30 bg-orange-500/15 text-orange-300'
    if (name.includes('ASE')) return 'border-violet-500/30 bg-violet-500/15 text-violet-300'
    if (name.includes('TSMC')) return 'border-emerald-500/30 bg-emerald-500/15 text-emerald-300'
    if (name.includes('TI')) return 'border-sky-500/30 bg-sky-500/15 text-sky-300'
    return 'border-border bg-muted text-muted-foreground'
  }

  function getOriginClasses(origin: ScheduleRow['origin']) {
    return origin === 'PULL_IN'
      ? 'border-violet-500/30 bg-violet-500/15 text-violet-300'
      : 'border-slate-500/30 bg-slate-500/15 text-slate-300'
  }

  function getGroupBadgeClasses(group: LineGroup) {
    if (groupBy.value === 'none') return 'border-border bg-muted text-muted-foreground'
    if (groupBy.value === 'supplier') {
      return getSupplierClasses(group.entries[0].line.supplier_name)
    }

    if (groupBy.value === 'status') {
      return getStatusClasses(group.entries[0].status)
    }

    return 'border-border bg-muted text-muted-foreground'
  }

  function getHistoryTone(record: PullInRow) {
    return record.quantity >= 1000 ? 'text-emerald-300' : 'text-violet-300'
  }

  function getReceiptTone(receipt: ReceiptRow) {
    return receipt.received_quantity > 1500 ? 'text-emerald-300' : 'text-foreground'
  }

  function getNextOpenSchedule(line: LineRow) {
    return (
      [...line.schedules]
        .filter((schedule) => getScheduleOpenQuantity(schedule) > 0)
        .sort((left, right) => left.commit_date.localeCompare(right.commit_date))[0] ?? null
    )
  }

  function getPrimaryEditableSchedule(line: LineRow) {
    return getNextOpenSchedule(line) ?? line.schedules[0] ?? null
  }

  function suggestEarlierDate(commitDate: string) {
    const date = new Date(commitDate)
    date.setDate(date.getDate() - 7)
    return date.toISOString().slice(0, 10)
  }

  function isGroupExpanded(groupKey: string) {
    return expandedGroupKeys.value.includes(groupKey)
  }

  function isLineExpanded(lineId: string) {
    return expandedLineIds.value.includes(lineId)
  }

  function toggleGroup(groupKey: string) {
    expandedGroupKeys.value = isGroupExpanded(groupKey)
      ? expandedGroupKeys.value.filter((key) => key !== groupKey)
      : [...expandedGroupKeys.value, groupKey]
  }

  function toggleLine(lineId: string) {
    expandedLineIds.value = isLineExpanded(lineId)
      ? expandedLineIds.value.filter((id) => id !== lineId)
      : [...expandedLineIds.value, lineId]
  }

  function isLineSelected(lineId: string) {
    return selectedLineIds.value.includes(lineId)
  }

  function toCheckedState(checked: CheckedState) {
    return checked === true
  }

  function getGroupCheckedState(group: LineGroup): CheckedState {
    const selectedCount = group.entries.filter((entry) => isLineSelected(entry.line.id)).length

    if (selectedCount === 0) return false
    if (selectedCount === group.entries.length) return true
    return 'indeterminate'
  }

  function updateLineSelection(lineId: string, checked: CheckedState) {
    if (toCheckedState(checked)) {
      selectedLineIds.value = Array.from(new Set([...selectedLineIds.value, lineId]))
      return
    }

    selectedLineIds.value = selectedLineIds.value.filter((selectedId) => selectedId !== lineId)
  }

  function updateGroupSelection(group: LineGroup, checked: CheckedState) {
    const groupLineIds = group.entries.map((entry) => entry.line.id)

    if (toCheckedState(checked)) {
      selectedLineIds.value = Array.from(new Set([...selectedLineIds.value, ...groupLineIds]))
      return
    }

    selectedLineIds.value = selectedLineIds.value.filter((lineId) => !groupLineIds.includes(lineId))
  }

  const isAllGroupsCollapsed = computed(
    () => groupBy.value !== 'none' && expandedGroupKeys.value.length === 0,
  )

  const isAllLinesExpanded = computed(() => {
    const visibleIds = visibleGroups.value.flatMap((g) => g.entries.map((e) => e.line.id))
    return visibleIds.length > 0 && visibleIds.every((id) => expandedLineIds.value.includes(id))
  })

  function toggleAllGroups() {
    if (groupBy.value === 'none') return
    if (isAllGroupsCollapsed.value) {
      expandedGroupKeys.value = visibleGroups.value.map((g) => g.key)
    } else {
      expandedGroupKeys.value = []
    }
  }

  function toggleAllDetails() {
    if (isAllLinesExpanded.value) {
      expandedLineIds.value = []
    } else {
      const visibleIds = visibleGroups.value.flatMap((g) => g.entries.map((e) => e.line.id))
      expandedLineIds.value = Array.from(new Set([...expandedLineIds.value, ...visibleIds]))
    }
  }

  function handleGroupChecked(group: LineGroup, checked: CheckedState) {
    updateGroupSelection(group, checked)
  }

  function handleLineChecked(lineId: string, checked: CheckedState) {
    updateLineSelection(lineId, checked)
  }

  function openPullInDialog(order: OrderRow, line: LineRow, schedule: ScheduleRow) {
    activePullInContext.value = { order, line, schedule }
    pullInForm.value = {
      target_date: suggestEarlierDate(schedule.commit_date),
      quantity: String(getScheduleOpenQuantity(schedule)),
      note: '',
      requested_by: 'Planner Team',
    }
    isPullInDialogOpen.value = true
  }

  function openPullInDialogForLine(order: OrderRow, line: LineRow) {
    const schedule = getNextOpenSchedule(line)
    if (!schedule) return
    openPullInDialog(order, line, schedule)
  }

  function closePullInDialog() {
    isPullInDialogOpen.value = false
    activePullInContext.value = null
  }

  function openScheduleDialog(order: OrderRow, line: LineRow, schedule: ScheduleRow) {
    activeScheduleContext.value = { order, line, schedule }
    scheduleForm.value = {
      commit_date: schedule.commit_date,
      quantity: String(schedule.quantity),
    }
    isScheduleDialogOpen.value = true
  }

  function openScheduleDialogForLine(order: OrderRow, line: LineRow) {
    const schedule = getPrimaryEditableSchedule(line)
    if (!schedule) return
    openScheduleDialog(order, line, schedule)
  }

  function closeScheduleDialog() {
    isScheduleDialogOpen.value = false
    activeScheduleContext.value = null
  }

  async function handlePullInSubmit() {
    if (!activePullInContext.value) return

    const { order, line, schedule } = activePullInContext.value
    const quantity = Number(pullInForm.value.quantity)
    const openQuantity = getScheduleOpenQuantity(schedule)

    if (!pullInForm.value.target_date) {
      toast.error(t('poManagement.validation.targetDateRequired'))
      return
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      toast.error(t('poManagement.validation.quantityPositive'))
      return
    }

    if (quantity > openQuantity) {
      toast.error(t('poManagement.validation.quantityExceeded'))
      return
    }

    if (pullInForm.value.target_date >= schedule.commit_date) {
      toast.error(t('poManagement.validation.targetDateEarlier'))
      return
    }

    try {
      await applyPullIn(order.id, line.id, schedule.id, {
        target_date: pullInForm.value.target_date,
        quantity,
        note: pullInForm.value.note,
        requested_by: pullInForm.value.requested_by,
      })
      toast.success(t('poManagement.toast.pullInSuccess'))
      closePullInDialog()
    } catch (pullInError) {
      toast.error(pullInError instanceof Error ? pullInError.message : t('toast.error'))
    }
  }

  async function handleScheduleSubmit() {
    if (!activeScheduleContext.value) return

    const { order, line, schedule } = activeScheduleContext.value
    const quantity = Number(scheduleForm.value.quantity)

    if (!scheduleForm.value.commit_date) {
      toast.error(t('poManagement.validation.commitDateRequired'))
      return
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      toast.error(t('poManagement.validation.scheduleQuantityPositive'))
      return
    }

    if (quantity < schedule.received_quantity) {
      toast.error(t('poManagement.validation.scheduleQuantityTooSmall'))
      return
    }

    try {
      await updateSchedule(order.id, line.id, schedule.id, {
        commit_date: scheduleForm.value.commit_date,
        quantity,
      })
      toast.success(t('poManagement.toast.scheduleUpdated'))
      closeScheduleDialog()
    } catch (scheduleError) {
      toast.error(scheduleError instanceof Error ? scheduleError.message : t('toast.error'))
    }
  }

  function handleResetFilters() {
    searchQuery.value = ''
    statusFilter.value = 'all'
    supplierFilter.value = 'all'
    sortBy.value = 'nextCommitAsc'
    groupBy.value = 'order'
  }

  async function handleResetDemo() {
    await resetDemoData()
    toast.success(t('poManagement.toast.resetSuccess'))
    selectedLineIds.value = []
  }
</script>

<template>
  <Tabs v-model="activeTab" class="flex flex-col gap-6 min-w-0 w-full">
    <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
          {{ $t('poManagement.title') }}
        </h1>
        <p class="mt-1 text-xs text-muted-foreground sm:text-sm">{{ $t('poManagement.subtitle') }}</p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <TabsList class="grid w-full grid-cols-2 sm:w-[320px]">
          <TabsTrigger value="list">{{ $t('poManagement.tabs.list') }}</TabsTrigger>
          <TabsTrigger value="calendar" disabled>{{
            $t('poManagement.tabs.calendar')
          }}</TabsTrigger>
        </TabsList>

        <div class="flex items-center gap-3 ml-auto sm:ml-0">
          <Badge
            variant="outline"
            class="hidden border-border/60 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-muted-foreground xs:flex"
          >
            {{ $t('poManagement.tabs.calendarSoon') }}
          </Badge>

          <Button variant="outline" size="sm" class="h-9" @click="handleResetDemo">
            <RotateCcw :size="14" data-icon="inline-start" />
            <span class="hidden sm:inline">{{ $t('poManagement.buttons.resetDemo') }}</span>
          </Button>
        </div>
      </div>
    </div>

    <Card class="border-border/70">
      <CardContent class="flex flex-col gap-4 p-4">
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-[minmax(0,1.3fr)_repeat(4,minmax(0,190px))_auto]">
          <div class="relative min-w-0 xl:col-span-1">
            <Search
              :size="16"
              class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <Input
              v-model="searchQuery"
              class="pl-9"
              :placeholder="$t('poManagement.searchPlaceholder')"
            />
          </div>

          <Select v-model="statusFilter">
            <SelectTrigger>
              <SelectValue :placeholder="$t('poManagement.controls.status')" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="all">{{ $t('poManagement.controls.allStatuses') }}</SelectItem>
                <SelectItem v-for="status in statusKeys" :key="status" :value="status">
                  {{ $t(`poManagement.status.${status}`) }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select v-model="supplierFilter">
            <SelectTrigger>
              <SelectValue :placeholder="$t('poManagement.controls.supplier')" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="all">{{ $t('poManagement.controls.allSuppliers') }}</SelectItem>
                <SelectItem v-for="supplier in supplierOptions" :key="supplier" :value="supplier">
                  {{ supplier }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select v-model="sortBy">
            <SelectTrigger>
              <SelectValue :placeholder="$t('poManagement.controls.sortBy')" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="option in sortOptions" :key="option.value" :value="option.value">
                  {{ $t(option.labelKey) }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select v-model="groupBy">
            <SelectTrigger>
              <SelectValue :placeholder="$t('poManagement.controls.groupBy')" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem
                  v-for="option in groupOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ $t(option.labelKey) }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm" class="w-full xl:w-auto" @click="handleResetFilters">
            <Filter :size="14" data-icon="inline-start" />
            {{ $t('poManagement.controls.resetFilters') }}
          </Button>
        </div>

        <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2">
          <Badge variant="outline" class="border-border/60 text-muted-foreground">
            {{ $t('poManagement.table.groupedBy') }}:
            {{
              $t(
                groupOptions.find((option) => option.value === groupBy)?.labelKey ??
                  'poManagement.controls.groupOrder',
              )
            }}
          </Badge>
          <Badge variant="outline" class="border-border/60 text-muted-foreground">
            {{
              $t(
                sortOptions.find((option) => option.value === sortBy)?.labelKey ??
                  'poManagement.controls.sortCommitAsc',
              )
            }}
          </Badge>
          <Badge
            v-if="statusFilter !== 'all'"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ $t(`poManagement.status.${statusFilter}`) }}
          </Badge>
          <Badge
            v-if="supplierFilter !== 'all'"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ supplierFilter }}
          </Badge>
          <Badge
            v-if="searchQuery.trim()"
            variant="outline"
            class="border-border/60 text-muted-foreground"
          >
            {{ searchQuery.trim() }}
          </Badge>
        </div>
      </CardContent>
    </Card>

    <TabsContent value="list" class="mt-0 flex flex-col gap-6 w-full min-w-0 overflow-hidden">
      <div
        v-if="error"
        class="flex items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive"
      >
        <AlertCircle :size="16" class="shrink-0" />
        <span>{{ error instanceof Error ? error.message : String(error) }}</span>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poManagement.stats.orders') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(orderCount) }}</CardTitle>
            </div>
            <PackageSearch :size="18" class="text-primary" />
          </CardHeader>
        </Card>

        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poManagement.stats.lines') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(lineCount) }}</CardTitle>
            </div>
            <Boxes :size="18" class="text-primary" />
          </CardHeader>
        </Card>

        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poManagement.stats.openQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalOpenQuantity) }}</CardTitle>
            </div>
            <Truck :size="18" class="text-primary" />
          </CardHeader>
        </Card>

        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poManagement.stats.pullInQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalPullInQuantity) }}</CardTitle>
            </div>
            <TrendingUpDown :size="18" class="text-primary" />
          </CardHeader>
        </Card>
      </div>

      <Card class="overflow-hidden border-border/70">
        <CardHeader class="border-b border-border/60 bg-muted/20">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div class="flex flex-col gap-1">
              <CardTitle class="text-base">{{ $t('poManagement.title') }}</CardTitle>
              <CardDescription>
                {{ $t('poManagement.table.groupedBy') }}
                {{
                  $t(
                    groupOptions.find((option) => option.value === groupBy)?.labelKey ??
                      'poManagement.controls.groupOrder',
                  )
                }}
              </CardDescription>
            </div>

            <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <Button v-if="groupBy !== 'none'" variant="ghost" size="xs" @click="toggleAllGroups" class="h-6 px-2 text-muted-foreground">
                <FolderTree :size="12" data-icon="inline-start" />
                {{ isAllGroupsCollapsed ? $t('poManagement.buttons.expandGroups') : $t('poManagement.buttons.collapseGroups') }}
              </Button>
              <Button variant="ghost" size="xs" @click="toggleAllDetails" class="h-6 px-2 text-muted-foreground">
                <ListTree :size="12" data-icon="inline-start" />
                {{ isAllLinesExpanded ? $t('poManagement.buttons.collapseDetails') : $t('poManagement.buttons.expandDetailsAll') }}
              </Button>
              <Badge variant="outline" class="border-border/60 text-muted-foreground">
                <ArrowUpDown :size="12" data-icon="inline-start" />
                {{
                  $t(
                    sortOptions.find((option) => option.value === sortBy)?.labelKey ??
                      'poManagement.controls.sortCommitAsc',
                  )
                }}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent class="p-0">
          <div
            v-if="isLoading"
            class="flex items-center justify-center gap-2 py-16 text-muted-foreground"
          >
            <RotateCcw :size="16" class="animate-spin" />
            <span>{{ $t('common.loading') }}</span>
          </div>

          <div
            v-else-if="visibleGroups.length === 0"
            class="flex items-center justify-center gap-2 py-16 text-muted-foreground"
          >
            <PackageSearch :size="18" />
            <span>{{ $t('poManagement.table.noData') }}</span>
          </div>

          <div v-else class="w-full relative min-w-0 overflow-x-auto scrollbar-thin">
            <Table class="min-w-[900px] xl:min-w-[1320px]">
              <TableHeader>
                <TableRow class="bg-muted/25 hover:bg-muted/25">
                  <TableHead :class="stickyHeaderCheckboxClass">&nbsp;</TableHead>
                  <TableHead :class="stickyHeaderPrimaryClass">{{
                    $t('poManagement.table.poLine')
                  }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.supplier') }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.orderDate') }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.nextCommitDate') }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.status') }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.itemName') }}</TableHead>
                  <TableHead>{{ $t('poManagement.table.metrics') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poManagement.table.actions') }}</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody v-for="group in visibleGroups" :key="group.key">
                <TableRow v-if="groupBy !== 'none'" class="bg-muted/20 hover:bg-muted/20">
                  <TableCell :class="stickyGroupCheckboxClass">
                    <Checkbox
                      :checked="getGroupCheckedState(group)"
                      :aria-label="`Select ${group.label}`"
                      @update:checked="handleGroupChecked(group, $event)"
                    />
                  </TableCell>

                  <TableCell :class="stickyGroupPrimaryClass">
                    <Button
                      variant="ghost"
                      size="xs"
                      class="h-8 px-2 text-foreground"
                      @click="toggleGroup(group.key)"
                    >
                      <component
                        :is="isGroupExpanded(group.key) ? ChevronDown : ChevronRight"
                        :size="14"
                        data-icon="inline-start"
                      />
                      {{ group.label }}
                    </Button>
                  </TableCell>

                  <TableCell colspan="7" class="bg-muted/20">
                    <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="outline" :class="cn('shrink-0', getGroupBadgeClasses(group))">
                        {{ group.badge }}
                      </Badge>
                      <span class="min-w-0 flex-1 truncate md:truncate-none lg:whitespace-normal">
                        {{ group.description }}
                      </span>
                    </div>
                  </TableCell>
                </TableRow>

                <template v-if="isGroupExpanded(group.key)">
                  <template v-for="entry in group.entries" :key="entry.line.id">
                    <TableRow class="group hover:bg-accent/20">
                      <TableCell :class="stickyLineCheckboxClass">
                        <Checkbox
                          :checked="isLineSelected(entry.line.id)"
                          :aria-label="`Select ${entry.order.order_number}-${entry.line.line_number}`"
                          @update:checked="handleLineChecked(entry.line.id, $event)"
                        />
                      </TableCell>

                      <TableCell :class="stickyLinePrimaryClass">
                        <div class="flex items-start gap-2">
                          <Button
                            variant="ghost"
                            size="xs"
                            class="mt-0.5 h-7 px-2 text-foreground"
                            @click="toggleLine(entry.line.id)"
                          >
                            <component
                              :is="isLineExpanded(entry.line.id) ? ChevronDown : ChevronRight"
                              :size="14"
                              data-icon="inline-start"
                            />
                            <RouterLink
                              :to="{ name: 'po-line-detail', params: { orderId: entry.order.id, lineId: entry.line.id } }"
                              class="hover:text-primary hover:underline"
                              @click.stop
                            >
                              {{ entry.order.order_number }}-{{ entry.line.line_number }}
                            </RouterLink>
                          </Button>
                        </div>
                        <RouterLink
                          :to="{ name: 'po-detail', params: { orderId: entry.order.id } }"
                          class="mt-1 block text-xs text-muted-foreground hover:text-primary hover:underline"
                        >
                          {{ entry.order.order_number }}
                        </RouterLink>
                      </TableCell>

                      <TableCell>
                        <Badge
                          variant="outline"
                          :class="getSupplierClasses(entry.line.supplier_name)"
                        >
                          {{ entry.line.supplier_name }}
                        </Badge>
                      </TableCell>

                      <TableCell class="text-muted-foreground">{{
                        entry.line.order_date
                      }}</TableCell>

                      <TableCell class="text-foreground">{{ entry.nextCommitDate }}</TableCell>

                      <TableCell>
                        <Badge variant="outline" :class="getStatusClasses(entry.status)">
                          {{ $t(`poManagement.status.${entry.status}`) }}
                        </Badge>
                      </TableCell>

                      <TableCell>
                        <div class="font-medium text-foreground">{{ entry.line.item_name }}</div>
                        <div class="mt-1 text-xs text-muted-foreground">{{ entry.line.notes }}</div>
                      </TableCell>

                      <TableCell>
                        <div class="grid gap-1 text-xs text-muted-foreground">
                          <div>
                            {{ $t('poManagement.table.open') }}:
                            <span class="text-foreground">{{
                              formatNumber(entry.openQuantity)
                            }}</span>
                          </div>
                          <div>
                            {{ $t('poManagement.table.received') }}:
                            <span class="text-foreground">{{
                              formatNumber(entry.receivedQuantity)
                            }}</span>
                          </div>
                          <div>
                            {{ $t('poManagement.table.pullInTotal') }}:
                            <span class="text-foreground">{{
                              formatNumber(entry.pullInQuantity)
                            }}</span>
                          </div>
                        </div>
                      </TableCell>

                      <TableCell class="min-w-[14rem] text-right align-top">
                        <div class="flex flex-wrap justify-end gap-2">
                          <Button
                            v-if="getPrimaryEditableSchedule(entry.line)"
                            variant="outline"
                            size="xs"
                            @click="openScheduleDialogForLine(entry.order, entry.line)"
                          >
                            <PencilLine :size="14" data-icon="inline-start" />
                            {{ $t('poManagement.buttons.editSchedule') }}
                          </Button>

                          <Button
                            v-if="getNextOpenSchedule(entry.line)"
                            variant="outline"
                            size="xs"
                            @click="openPullInDialogForLine(entry.order, entry.line)"
                          >
                            <TrendingUpDown :size="14" data-icon="inline-start" />
                            {{ $t('poManagement.buttons.pullIn') }}
                          </Button>

                          <Button variant="ghost" size="xs" @click="toggleLine(entry.line.id)">
                            {{ $t('poManagement.buttons.expandDetails') }}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>

                    <TableRow v-if="isLineExpanded(entry.line.id)" class="hover:bg-transparent tracking-normal">
                      <TableCell colspan="9" class="p-0 align-top relative">
                        <div class="sticky left-0 w-full min-w-[320px] md:min-w-[700px] border-b border-border/50 bg-background/50 backdrop-blur p-4 pl-14 pr-4 xl:pl-16">
                          <div class="grid gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)]">
                          <Card class="overflow-hidden border-border/60 bg-background/80">
                            <CardHeader class="border-b border-border/60 pb-4">
                              <div class="flex items-center justify-between gap-3">
                                <div class="flex flex-col gap-1">
                                  <CardTitle class="text-sm">{{
                                    $t('poManagement.detail.deliverySplit')
                                  }}</CardTitle>
                                  <CardDescription>{{ entry.line.notes }}</CardDescription>
                                </div>
                                <CalendarRange :size="16" class="text-primary" />
                              </div>
                            </CardHeader>

                            <CardContent class="p-0">
                              <Table class="min-w-[720px]">
                                <TableHeader>
                                  <TableRow class="bg-muted/20 hover:bg-muted/20">
                                    <TableHead>{{
                                      $t('poManagement.detail.scheduleNo')
                                    }}</TableHead>
                                    <TableHead>{{
                                      $t('poManagement.detail.commitDate')
                                    }}</TableHead>
                                    <TableHead>{{ $t('poManagement.detail.qty') }}</TableHead>
                                    <TableHead>{{
                                      $t('poManagement.detail.receivedQty')
                                    }}</TableHead>
                                    <TableHead>{{ $t('poManagement.detail.openQty') }}</TableHead>
                                    <TableHead>{{ $t('poManagement.detail.origin') }}</TableHead>
                                    <TableHead class="text-right">{{
                                      $t('poManagement.table.actions')
                                    }}</TableHead>
                                  </TableRow>
                                </TableHeader>

                                <TableBody>
                                  <TableRow
                                    v-for="schedule in entry.line.schedules"
                                    :key="schedule.id"
                                  >
                                    <TableCell class="font-medium text-foreground">
                                      {{ schedule.schedule_no }}
                                    </TableCell>
                                    <TableCell class="text-muted-foreground">
                                      {{ schedule.commit_date }}
                                    </TableCell>
                                    <TableCell>{{ formatNumber(schedule.quantity) }}</TableCell>
                                    <TableCell>{{
                                      formatNumber(schedule.received_quantity)
                                    }}</TableCell>
                                    <TableCell>{{
                                      formatNumber(getScheduleOpenQuantity(schedule))
                                    }}</TableCell>
                                    <TableCell>
                                      <Badge
                                        variant="outline"
                                        :class="getOriginClasses(schedule.origin)"
                                      >
                                        {{
                                          $t(
                                            `poManagement.status.${schedule.origin === 'PULL_IN' ? 'pullIn' : 'original'}`,
                                          )
                                        }}
                                      </Badge>
                                    </TableCell>
                                    <TableCell class="text-right">
                                      <div class="flex flex-wrap justify-end gap-2">
                                        <Button
                                          variant="outline"
                                          size="xs"
                                          @click="
                                            openScheduleDialog(entry.order, entry.line, schedule)
                                          "
                                        >
                                          <PencilLine :size="14" data-icon="inline-start" />
                                          {{ $t('poManagement.buttons.editSchedule') }}
                                        </Button>
                                        <Button
                                          v-if="getScheduleOpenQuantity(schedule) > 0"
                                          variant="outline"
                                          size="xs"
                                          @click="
                                            openPullInDialog(entry.order, entry.line, schedule)
                                          "
                                        >
                                          <TrendingUpDown :size="14" data-icon="inline-start" />
                                          {{ $t('poManagement.buttons.pullIn') }}
                                        </Button>
                                      </div>
                                    </TableCell>
                                  </TableRow>
                                </TableBody>
                              </Table>
                            </CardContent>
                          </Card>

                          <div class="flex flex-col gap-4">
                            <Card class="overflow-hidden border-border/60 bg-background/80">
                              <CardHeader class="border-b border-border/60 pb-4">
                                <div class="flex items-center justify-between gap-3">
                                  <div class="flex flex-col gap-1">
                                    <CardTitle class="text-sm">{{
                                      $t('poManagement.detail.receiptRecords')
                                    }}</CardTitle>
                                    <CardDescription
                                      >{{ entry.receiptCount }} receipts</CardDescription
                                    >
                                  </div>
                                  <ReceiptText :size="16" class="text-primary" />
                                </div>
                              </CardHeader>

                              <CardContent class="flex flex-col gap-3 p-4">
                                <div
                                  v-if="getLineReceipts(entry.line).length === 0"
                                  class="text-sm text-muted-foreground"
                                >
                                  {{ $t('poManagement.detail.noReceipts') }}
                                </div>

                                <template v-else>
                                  <div
                                    v-for="receipt in getLineReceipts(entry.line)"
                                    :key="receipt.id"
                                    class="rounded-lg border border-border/50 bg-muted/20 px-3 py-3"
                                  >
                                    <div class="flex items-center justify-between gap-3 text-sm">
                                      <div>
                                        <div class="font-medium text-foreground">
                                          {{ receipt.receipt_number }}
                                        </div>
                                        <div class="mt-1 text-xs text-muted-foreground">
                                          {{ receipt.schedule_no }} · {{ receipt.received_date }}
                                        </div>
                                      </div>
                                      <div
                                        class="text-right text-sm font-medium"
                                        :class="getReceiptTone(receipt)"
                                      >
                                        {{ formatNumber(receipt.received_quantity) }}
                                      </div>
                                    </div>
                                  </div>
                                </template>
                              </CardContent>
                            </Card>

                            <Card class="overflow-hidden border-border/60 bg-background/80">
                              <CardHeader class="border-b border-border/60 pb-4">
                                <div class="flex items-center justify-between gap-3">
                                  <div class="flex flex-col gap-1">
                                    <CardTitle class="text-sm">{{
                                      $t('poManagement.detail.pullInHistory')
                                    }}</CardTitle>
                                    <CardDescription>
                                      {{ formatNumber(entry.pullInQuantity) }}
                                      {{ $t('poManagement.table.pullInTotal') }}
                                    </CardDescription>
                                  </div>
                                  <History :size="16" class="text-primary" />
                                </div>
                              </CardHeader>

                              <CardContent class="flex flex-col gap-3 p-4">
                                <div
                                  v-if="entry.line.pull_in_records.length === 0"
                                  class="text-sm text-muted-foreground"
                                >
                                  {{ $t('poManagement.detail.noPullIn') }}
                                </div>

                                <template v-else>
                                  <div
                                    v-for="record in entry.line.pull_in_records"
                                    :key="record.id"
                                    class="rounded-lg border border-border/50 bg-muted/20 px-3 py-3"
                                  >
                                    <div class="flex items-start justify-between gap-3">
                                      <div>
                                        <div class="text-sm font-medium text-foreground">
                                          {{ record.previous_commit_date }} →
                                          {{ record.target_date }}
                                        </div>
                                        <div class="mt-1 text-xs text-muted-foreground">
                                          {{ record.created_by }} ·
                                          {{ record.created_at.slice(0, 10) }}
                                        </div>
                                        <div
                                          v-if="record.note"
                                          class="mt-2 text-xs text-muted-foreground"
                                        >
                                          {{ record.note }}
                                        </div>
                                      </div>
                                      <div
                                        class="text-right text-sm font-medium"
                                        :class="getHistoryTone(record)"
                                      >
                                        {{ formatNumber(record.quantity) }}
                                      </div>
                                    </div>
                                  </div>
                                </template>
                              </CardContent>
                            </Card>
                            </div>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  </template>
                </template>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </TabsContent>

    <TabsContent value="calendar" class="mt-0">
      <Card class="border-dashed border-border/70">
        <CardContent class="flex items-center gap-3 p-6 text-sm text-muted-foreground">
          <CalendarRange :size="16" />
          {{ $t('poManagement.tabs.calendarSoon') }}
        </CardContent>
      </Card>
    </TabsContent>

    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 md:translate-y-8"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4 md:translate-y-8"
    >
      <div
        v-if="selectedLineIds.length > 0"
        class="fixed bottom-8 left-1/2 z-[100] flex -translate-x-1/2 items-center gap-3 md:gap-5 rounded-full border border-border bg-popover/95 px-4 md:px-6 py-2 md:py-3 shadow-2xl shadow-black/20 backdrop-blur dark:shadow-black/60"
      >
        <div class="flex items-center gap-2">
          <span
            class="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground"
          >
            {{ selectedLineIds.length }}
          </span>
          <span class="text-sm font-medium text-foreground hidden sm:inline">
            {{ $t('poManagement.table.itemsSelected') }}
          </span>
        </div>
        <div class="h-5 w-px bg-border text-border"></div>
        <Button variant="ghost" size="xs" class="text-muted-foreground hover:text-foreground h-7">
          <Mail class="text-emerald-500" :size="16" data-icon="inline-start" />
          <span class="hidden sm:inline">{{ $t('poManagement.buttons.batchUrge') }}</span>
        </Button>
        <Button variant="ghost" size="xs" class="text-muted-foreground hover:text-foreground h-7">
          <CalendarClock class="text-orange-500" :size="16" data-icon="inline-start" />
          <span class="hidden sm:inline">{{ $t('poManagement.buttons.pushOut') }}</span>
        </Button>
        <Button variant="ghost" size="xs" class="text-muted-foreground hover:text-foreground h-7">
          <Download class="text-primary" :size="16" data-icon="inline-start" />
          <span class="hidden sm:inline">{{ $t('poManagement.buttons.export') }}</span>
        </Button>
        <div class="h-5 w-px bg-border text-border"></div>
        <Button
          variant="ghost"
          size="xs"
          class="text-muted-foreground hover:text-destructive h-7"
          @click="selectedLineIds = []"
        >
          <XCircle :size="16" data-icon="inline-start" />
          <span class="hidden sm:inline">{{ $t('poManagement.buttons.cancel') }}</span>
        </Button>
      </div>
    </transition>

    <Dialog v-model:open="isScheduleDialogOpen">
      <DialogContent class="sm:max-w-lg">
        <DialogTitle>{{ $t('poManagement.scheduleDialog.title') }}</DialogTitle>
        <DialogDescription>{{ $t('poManagement.scheduleDialog.description') }}</DialogDescription>

        <div v-if="activeScheduleContext" class="grid gap-4 py-2">
          <div class="grid gap-3 rounded-lg border border-border/60 bg-muted/20 p-4 sm:grid-cols-2">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {{ $t('poManagement.scheduleDialog.scheduleNo') }}
              </div>
              <div class="mt-2 font-medium text-foreground">
                {{ activeScheduleContext.schedule.schedule_no }}
              </div>
            </div>

            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {{ $t('poManagement.scheduleDialog.receivedQty') }}
              </div>
              <div class="mt-2 font-medium text-foreground">
                {{ formatNumber(activeScheduleContext.schedule.received_quantity) }}
              </div>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="grid gap-2">
              <Label for="schedule-commit-date">{{
                $t('poManagement.scheduleDialog.commitDate')
              }}</Label>
              <Input id="schedule-commit-date" v-model="scheduleForm.commit_date" type="date" />
            </div>

            <div class="grid gap-2">
              <Label for="schedule-quantity">{{
                $t('poManagement.scheduleDialog.quantity')
              }}</Label>
              <Input
                id="schedule-quantity"
                v-model="scheduleForm.quantity"
                min="1"
                step="1"
                type="number"
              />
            </div>
          </div>
        </div>

        <DialogFooter class="mt-2 flex gap-2 sm:justify-end">
          <Button variant="ghost" @click="closeScheduleDialog">
            {{ $t('poManagement.scheduleDialog.cancel') }}
          </Button>
          <Button @click="handleScheduleSubmit">
            {{ $t('poManagement.scheduleDialog.confirm') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isPullInDialogOpen">
      <DialogContent class="sm:max-w-lg">
        <DialogTitle>{{ $t('poManagement.dialog.title') }}</DialogTitle>
        <DialogDescription>{{ $t('poManagement.dialog.description') }}</DialogDescription>

        <div v-if="activePullInContext" class="grid gap-4 py-2">
          <div class="grid gap-3 rounded-lg border border-border/60 bg-muted/20 p-4 sm:grid-cols-2">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {{ $t('poManagement.dialog.sourceCommitDate') }}
              </div>
              <div class="mt-2 font-medium text-foreground">
                {{ activePullInContext.schedule.commit_date }}
              </div>
            </div>

            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {{ $t('poManagement.dialog.openQty') }}
              </div>
              <div class="mt-2 font-medium text-foreground">
                {{ formatNumber(getScheduleOpenQuantity(activePullInContext.schedule)) }}
              </div>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="grid gap-2">
              <Label for="pull-in-target-date">{{ $t('poManagement.dialog.targetDate') }}</Label>
              <Input id="pull-in-target-date" v-model="pullInForm.target_date" type="date" />
            </div>

            <div class="grid gap-2">
              <Label for="pull-in-quantity">{{ $t('poManagement.dialog.quantity') }}</Label>
              <Input
                id="pull-in-quantity"
                v-model="pullInForm.quantity"
                min="1"
                step="1"
                type="number"
              />
            </div>
          </div>

          <div class="grid gap-2">
            <Label for="pull-in-requester">{{ $t('poManagement.dialog.requester') }}</Label>
            <Input id="pull-in-requester" v-model="pullInForm.requested_by" />
          </div>

          <div class="grid gap-2">
            <Label for="pull-in-note">{{ $t('poManagement.dialog.note') }}</Label>
            <Textarea id="pull-in-note" v-model="pullInForm.note" class="min-h-24" />
          </div>
        </div>

        <DialogFooter class="mt-2 flex gap-2 sm:justify-end">
          <Button variant="ghost" @click="closePullInDialog">
            {{ $t('poManagement.dialog.cancel') }}
          </Button>
          <Button @click="handlePullInSubmit">
            {{ $t('poManagement.dialog.confirm') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Tabs>
</template>
