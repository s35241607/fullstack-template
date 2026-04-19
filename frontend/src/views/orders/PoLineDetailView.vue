<script setup lang="ts">
  import { computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useI18n } from 'vue-i18n'

  import { usePoManagement } from '@/composables/usePoManagement'
  import { cn } from '@/lib/utils'
  import type { PurchaseOrderSchedule } from '@/services/api'

  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from '@/components/ui/table'
  import {
    ArrowLeft,
    CalendarRange,
    Boxes,
    PackageSearch,
    ReceiptText,
    RotateCcw,
    TrendingUpDown,
    FileText,
    Building2,
    CalendarDays,
    Tag,
    Package,
  } from 'lucide-vue-next'

  type StatusKey = 'completed' | 'partial' | 'delayed' | 'inTransit' | 'newArrival' | 'pullInPlanned'

  const route = useRoute()
  const router = useRouter()
  useI18n()
  const { orders, isLoading } = usePoManagement()

  const orderId = computed(() => route.params.orderId as string)
  const lineId = computed(() => route.params.lineId as string)

  const order = computed(() => orders.value.find((o) => o.id === orderId.value) ?? null)
  const line = computed(() => order.value?.lines.find((l) => l.id === lineId.value) ?? null)

  const scheduleCount = computed(() => line.value?.schedules.length ?? 0)

  const totalOpenQty = computed(() =>
    (line.value?.schedules ?? []).reduce(
      (sum, sch) => sum + Math.max(sch.quantity - sch.received_quantity, 0),
      0,
    ),
  )

  const totalReceivedQty = computed(() =>
    (line.value?.schedules ?? []).reduce((sum, sch) => sum + sch.received_quantity, 0),
  )

  const pullInCount = computed(() => line.value?.pull_in_records.length ?? 0)

  interface ReceiptDetail {
    id: string
    receipt_number: string
    received_date: string
    received_quantity: number
    schedule_no: string
  }

  const allReceipts = computed<ReceiptDetail[]>(() =>
    (line.value?.schedules ?? []).flatMap((sch) =>
      sch.receipts.map((r) => ({
        ...r,
        schedule_no: sch.schedule_no,
      })),
    ),
  )

  function formatNumber(value: number) {
    return new Intl.NumberFormat('en-US').format(value)
  }

  function getScheduleOpenQty(schedule: PurchaseOrderSchedule) {
    return Math.max(schedule.quantity - schedule.received_quantity, 0)
  }

  function getScheduleProgress(schedule: PurchaseOrderSchedule) {
    if (schedule.quantity === 0) return 0
    return Math.round((schedule.received_quantity / schedule.quantity) * 100)
  }

  function getOriginClasses(origin: PurchaseOrderSchedule['origin']) {
    return origin === 'PULL_IN'
      ? 'border-violet-500/30 bg-violet-500/15 text-violet-300'
      : 'border-slate-500/30 bg-slate-500/15 text-slate-300'
  }

  function getProgressBarClasses(progress: number) {
    if (progress >= 100) return 'bg-emerald-500'
    if (progress >= 50) return 'bg-amber-500'
    return 'bg-blue-500'
  }

  function getLineStatus(): StatusKey {
    if (!line.value) return 'newArrival'
    const openQty = totalOpenQty.value
    const receivedQty = totalReceivedQty.value
    const pullInQty = line.value.pull_in_records.reduce((s, r) => s + r.quantity, 0)
    const nextSchedule = [...line.value.schedules]
      .filter((s) => getScheduleOpenQty(s) > 0)
      .sort((a, b) => a.commit_date.localeCompare(b.commit_date))[0]
    const nextCommitDate = nextSchedule?.commit_date ?? line.value.schedules[0]?.commit_date ?? ''
    const today = new Date().toISOString().slice(0, 10)

    if (openQty === 0) return 'completed'
    if (nextCommitDate < today) return 'delayed'
    if (pullInQty > 0) return 'pullInPlanned'
    if (receivedQty > 0) return 'partial'
    if (nextCommitDate <= '2026-04-30') return 'inTransit'
    return 'newArrival'
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
</script>

<template>
  <div class="flex flex-col gap-6 min-w-0 w-full">
    <!-- Loading -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center gap-2 py-16 text-muted-foreground"
    >
      <RotateCcw :size="16" class="animate-spin" />
      <span>{{ $t('common.loading') }}</span>
    </div>

    <!-- Not found -->
    <div
      v-else-if="!order || !line"
      class="flex flex-col items-center justify-center gap-4 py-16 text-muted-foreground"
    >
      <PackageSearch :size="48" class="text-muted-foreground/50" />
      <div class="text-center">
        <p class="text-lg font-medium text-foreground">{{ $t('poLineDetail.notFound') }}</p>
        <p class="mt-1 text-sm">{{ $t('poLineDetail.notFoundDesc') }}</p>
      </div>
      <Button
        variant="outline"
        @click="router.push(order ? { name: 'po-detail', params: { orderId } } : { name: 'po-management' })"
      >
        <ArrowLeft :size="14" data-icon="inline-start" />
        {{ $t('poLineDetail.backToOrder') }}
      </Button>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon-sm"
            @click="router.push({ name: 'po-detail', params: { orderId } })"
          >
            <ArrowLeft :size="16" />
          </Button>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                {{ order.order_number }}-{{ line.line_number }}
              </h1>
              <Badge variant="outline" :class="getStatusClasses(getLineStatus())">
                {{ $t(`poManagement.status.${getLineStatus()}`) }}
              </Badge>
            </div>
            <p class="mt-0.5 text-xs text-muted-foreground sm:text-sm">
              {{ line.item_name }} · {{ line.item_code }}
            </p>
          </div>
        </div>
      </div>

      <!-- Line Info Card -->
      <Card class="border-border/70">
        <CardHeader class="pb-3">
          <CardTitle class="text-base">{{ $t('poLineDetail.lineInfo') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText :size="12" />
                {{ $t('poLineDetail.poNumber') }}
              </span>
              <RouterLink
                :to="{ name: 'po-detail', params: { orderId } }"
                class="text-sm font-medium text-primary hover:underline"
              >
                {{ order.order_number }}
              </RouterLink>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Tag :size="12" />
                {{ $t('poLineDetail.lineNumber') }}
              </span>
              <span class="text-sm font-medium">{{ line.line_number }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Building2 :size="12" />
                {{ $t('poLineDetail.supplier') }}
              </span>
              <Badge variant="outline" :class="cn('w-fit', getSupplierClasses(line.supplier_name))">
                {{ line.supplier_name }}
              </Badge>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Package :size="12" />
                {{ $t('poLineDetail.itemCode') }}
              </span>
              <span class="text-sm font-medium">{{ line.item_code }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <CalendarDays :size="12" />
                {{ $t('poLineDetail.orderDate') }}
              </span>
              <span class="text-sm font-medium">{{ line.order_date }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText :size="12" />
                {{ $t('poLineDetail.notes') }}
              </span>
              <span class="text-sm font-medium">{{ line.notes || '—' }}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poLineDetail.stats.schedules') }}</CardDescription>
              <CardTitle class="text-2xl">{{ scheduleCount }}</CardTitle>
            </div>
            <Boxes :size="18" class="text-primary" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poLineDetail.stats.openQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalOpenQty) }}</CardTitle>
            </div>
            <CalendarRange :size="18" class="text-amber-400" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poLineDetail.stats.receivedQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalReceivedQty) }}</CardTitle>
            </div>
            <ReceiptText :size="18" class="text-emerald-400" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poLineDetail.stats.pullInCount') }}</CardDescription>
              <CardTitle class="text-2xl">{{ pullInCount }}</CardTitle>
            </div>
            <TrendingUpDown :size="18" class="text-violet-400" />
          </CardHeader>
        </Card>
      </div>

      <!-- Delivery Schedules -->
      <Card class="overflow-hidden border-border/70">
        <CardHeader class="border-b border-border/60 bg-muted/20">
          <CardTitle class="text-base">{{ $t('poLineDetail.scheduleTitle') }}</CardTitle>
          <CardDescription>{{ $t('poLineDetail.scheduleSubtitle') }}</CardDescription>
        </CardHeader>
        <CardContent class="p-0">
          <div class="w-full min-w-0 overflow-x-auto scrollbar-thin">
            <Table>
              <TableHeader>
                <TableRow class="bg-muted/25 hover:bg-muted/25">
                  <TableHead>{{ $t('poLineDetail.scheduleTable.scheduleNo') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.scheduleTable.commitDate') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poLineDetail.scheduleTable.quantity') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poLineDetail.scheduleTable.receivedQty') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poLineDetail.scheduleTable.openQty') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.scheduleTable.origin') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.scheduleTable.progress') }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="sch in line.schedules" :key="sch.id" class="hover:bg-accent/20">
                  <TableCell class="font-medium">{{ sch.schedule_no }}</TableCell>
                  <TableCell>{{ sch.commit_date }}</TableCell>
                  <TableCell class="text-right tabular-nums">{{ formatNumber(sch.quantity) }}</TableCell>
                  <TableCell class="text-right tabular-nums">{{ formatNumber(sch.received_quantity) }}</TableCell>
                  <TableCell class="text-right tabular-nums">{{ formatNumber(getScheduleOpenQty(sch)) }}</TableCell>
                  <TableCell>
                    <Badge variant="outline" :class="getOriginClasses(sch.origin)">
                      {{ $t(`poManagement.status.${sch.origin === 'PULL_IN' ? 'pullIn' : 'original'}`) }}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div class="flex items-center gap-2">
                      <div class="h-2 w-20 rounded-full bg-muted">
                        <div
                          class="h-full rounded-full transition-all"
                          :class="getProgressBarClasses(getScheduleProgress(sch))"
                          :style="{ width: `${Math.min(getScheduleProgress(sch), 100)}%` }"
                        />
                      </div>
                      <span class="text-xs tabular-nums text-muted-foreground">
                        {{ getScheduleProgress(sch) }}%
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <!-- Receipt Records -->
      <Card class="overflow-hidden border-border/70">
        <CardHeader class="border-b border-border/60 bg-muted/20">
          <CardTitle class="text-base">{{ $t('poLineDetail.receiptTitle') }}</CardTitle>
          <CardDescription>{{ $t('poLineDetail.receiptSubtitle') }}</CardDescription>
        </CardHeader>
        <CardContent class="p-0">
          <div v-if="allReceipts.length === 0" class="flex items-center justify-center gap-2 py-12 text-muted-foreground">
            <ReceiptText :size="16" />
            <span>{{ $t('poLineDetail.noReceipts') }}</span>
          </div>
          <div v-else class="w-full min-w-0 overflow-x-auto scrollbar-thin">
            <Table>
              <TableHeader>
                <TableRow class="bg-muted/25 hover:bg-muted/25">
                  <TableHead>{{ $t('poLineDetail.receiptTable.receiptNo') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.receiptTable.receiptDate') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poLineDetail.receiptTable.receivedQty') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.receiptTable.scheduleNo') }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="receipt in allReceipts" :key="receipt.id" class="hover:bg-accent/20">
                  <TableCell class="font-medium">{{ receipt.receipt_number }}</TableCell>
                  <TableCell>{{ receipt.received_date }}</TableCell>
                  <TableCell class="text-right tabular-nums">{{ formatNumber(receipt.received_quantity) }}</TableCell>
                  <TableCell>
                    <Badge variant="outline" class="border-border bg-muted text-muted-foreground">
                      {{ receipt.schedule_no }}
                    </Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <!-- Pull In History -->
      <Card class="overflow-hidden border-border/70">
        <CardHeader class="border-b border-border/60 bg-muted/20">
          <CardTitle class="text-base">{{ $t('poLineDetail.pullInTitle') }}</CardTitle>
          <CardDescription>{{ $t('poLineDetail.pullInSubtitle') }}</CardDescription>
        </CardHeader>
        <CardContent class="p-0">
          <div v-if="line.pull_in_records.length === 0" class="flex items-center justify-center gap-2 py-12 text-muted-foreground">
            <TrendingUpDown :size="16" />
            <span>{{ $t('poLineDetail.noPullIn') }}</span>
          </div>
          <div v-else class="w-full min-w-0 overflow-x-auto scrollbar-thin">
            <Table>
              <TableHeader>
                <TableRow class="bg-muted/25 hover:bg-muted/25">
                  <TableHead>{{ $t('poLineDetail.pullInTable.previousDate') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.pullInTable.targetDate') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poLineDetail.pullInTable.quantity') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.pullInTable.note') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.pullInTable.requestedBy') }}</TableHead>
                  <TableHead>{{ $t('poLineDetail.pullInTable.createdAt') }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="record in line.pull_in_records" :key="record.id" class="hover:bg-accent/20">
                  <TableCell class="text-muted-foreground">{{ record.previous_commit_date }}</TableCell>
                  <TableCell class="font-medium">{{ record.target_date }}</TableCell>
                  <TableCell class="text-right tabular-nums">{{ formatNumber(record.quantity) }}</TableCell>
                  <TableCell class="max-w-[200px] truncate">{{ record.note || '—' }}</TableCell>
                  <TableCell>{{ record.created_by }}</TableCell>
                  <TableCell class="text-muted-foreground">{{ record.created_at.slice(0, 10) }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
