<script setup lang="ts">
  import { computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useI18n } from 'vue-i18n'

  import { usePoManagement } from '@/composables/usePoManagement'
  import type { PurchaseOrderLine, PurchaseOrderSchedule } from '@/services/api'

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
    Boxes,
    CalendarRange,
    ExternalLink,
    PackageSearch,
    ReceiptText,
    RotateCcw,
    TrendingUpDown,
    User,
    FileText,
    Coins,
    CalendarDays,
    Building2,
  } from 'lucide-vue-next'

  type StatusKey = 'completed' | 'partial' | 'delayed' | 'inTransit' | 'newArrival' | 'pullInPlanned'

  const route = useRoute()
  const router = useRouter()
  useI18n()
  const { orders, isLoading } = usePoManagement()

  const orderId = computed(() => route.params.orderId as string)

  const order = computed(() => orders.value.find((o) => o.id === orderId.value) ?? null)

  const totalLines = computed(() => order.value?.lines.length ?? 0)

  const totalOpenQty = computed(() =>
    (order.value?.lines ?? []).reduce(
      (sum, line) =>
        sum +
        line.schedules.reduce(
          (s, sch) => s + Math.max(sch.quantity - sch.received_quantity, 0),
          0,
        ),
      0,
    ),
  )

  const totalReceivedQty = computed(() =>
    (order.value?.lines ?? []).reduce(
      (sum, line) =>
        sum + line.schedules.reduce((s, sch) => s + sch.received_quantity, 0),
      0,
    ),
  )

  const totalPullInQty = computed(() =>
    (order.value?.lines ?? []).reduce(
      (sum, line) =>
        sum + line.pull_in_records.reduce((s, r) => s + r.quantity, 0),
      0,
    ),
  )

  function formatNumber(value: number) {
    return new Intl.NumberFormat('en-US').format(value)
  }

  function getScheduleOpenQty(schedule: PurchaseOrderSchedule) {
    return Math.max(schedule.quantity - schedule.received_quantity, 0)
  }

  function getLineOpenQty(line: PurchaseOrderLine) {
    return line.schedules.reduce((total, sch) => total + getScheduleOpenQty(sch), 0)
  }

  function getLineReceivedQty(line: PurchaseOrderLine) {
    return line.schedules.reduce((total, sch) => total + sch.received_quantity, 0)
  }

  function getLineNextCommitDate(line: PurchaseOrderLine) {
    const next = [...line.schedules]
      .filter((s) => getScheduleOpenQty(s) > 0)
      .sort((a, b) => a.commit_date.localeCompare(b.commit_date))[0]
    return next?.commit_date ?? line.schedules[0]?.commit_date ?? '—'
  }

  function getLineStatus(line: PurchaseOrderLine): StatusKey {
    const openQty = getLineOpenQty(line)
    const receivedQty = getLineReceivedQty(line)
    const pullInQty = line.pull_in_records.reduce((s, r) => s + r.quantity, 0)
    const nextCommitDate = getLineNextCommitDate(line)
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

  function navigateToLine(lineId: string) {
    router.push({
      name: 'po-line-detail',
      params: { orderId: orderId.value, lineId },
    })
  }
</script>

<template>
  <div class="flex flex-col gap-6 min-w-0 w-full">
    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center gap-2 py-16 text-muted-foreground"
    >
      <RotateCcw :size="16" class="animate-spin" />
      <span>{{ $t('common.loading') }}</span>
    </div>

    <!-- Not found -->
    <div
      v-else-if="!order"
      class="flex flex-col items-center justify-center gap-4 py-16 text-muted-foreground"
    >
      <PackageSearch :size="48" class="text-muted-foreground/50" />
      <div class="text-center">
        <p class="text-lg font-medium text-foreground">{{ $t('poDetail.notFound') }}</p>
        <p class="mt-1 text-sm">{{ $t('poDetail.notFoundDesc') }}</p>
      </div>
      <Button variant="outline" @click="router.push({ name: 'po-management' })">
        <ArrowLeft :size="14" data-icon="inline-start" />
        {{ $t('poDetail.backToList') }}
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
            @click="router.push({ name: 'po-management' })"
          >
            <ArrowLeft :size="16" />
          </Button>
          <div>
            <h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
              {{ order.order_number }}
            </h1>
            <p class="mt-0.5 text-xs text-muted-foreground sm:text-sm">
              {{ order.notes }}
            </p>
          </div>
        </div>
      </div>

      <!-- Order Info Card -->
      <Card class="border-border/70">
        <CardHeader class="pb-3">
          <CardTitle class="text-base">{{ $t('poDetail.orderInfo') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText :size="12" />
                {{ $t('poDetail.orderNumber') }}
              </span>
              <span class="text-sm font-medium">{{ order.order_number }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Building2 :size="12" />
                {{ $t('poDetail.supplier') }}
              </span>
              <span class="text-sm font-medium">{{ order.supplier_name }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <CalendarDays :size="12" />
                {{ $t('poDetail.orderDate') }}
              </span>
              <span class="text-sm font-medium">{{ order.order_date }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <User :size="12" />
                {{ $t('poDetail.buyer') }}
              </span>
              <span class="text-sm font-medium">{{ order.buyer_name }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Coins :size="12" />
                {{ $t('poDetail.currency') }}
              </span>
              <span class="text-sm font-medium">{{ order.currency }}</span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText :size="12" />
                {{ $t('poDetail.notes') }}
              </span>
              <span class="text-sm font-medium">{{ order.notes || '—' }}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poDetail.stats.totalLines') }}</CardDescription>
              <CardTitle class="text-2xl">{{ totalLines }}</CardTitle>
            </div>
            <Boxes :size="18" class="text-primary" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poDetail.stats.openQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalOpenQty) }}</CardTitle>
            </div>
            <CalendarRange :size="18" class="text-amber-400" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poDetail.stats.receivedQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalReceivedQty) }}</CardTitle>
            </div>
            <ReceiptText :size="18" class="text-emerald-400" />
          </CardHeader>
        </Card>
        <Card class="border-border/70">
          <CardHeader class="flex flex-row items-start justify-between gap-3 pb-3">
            <div class="flex flex-col gap-1">
              <CardDescription>{{ $t('poDetail.stats.pullInQty') }}</CardDescription>
              <CardTitle class="text-2xl">{{ formatNumber(totalPullInQty) }}</CardTitle>
            </div>
            <TrendingUpDown :size="18" class="text-violet-400" />
          </CardHeader>
        </Card>
      </div>

      <!-- Lines Table -->
      <Card class="overflow-hidden border-border/70">
        <CardHeader class="border-b border-border/60 bg-muted/20">
          <CardTitle class="text-base">{{ $t('poDetail.linesTitle') }}</CardTitle>
          <CardDescription>{{ $t('poDetail.linesSubtitle') }}</CardDescription>
        </CardHeader>
        <CardContent class="p-0">
          <div class="w-full min-w-0 overflow-x-auto scrollbar-thin">
            <Table class="min-w-[800px]">
              <TableHeader>
                <TableRow class="bg-muted/25 hover:bg-muted/25">
                  <TableHead>{{ $t('poDetail.table.lineNumber') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.supplier') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.itemCode') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.itemName') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.orderDate') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.nextCommitDate') }}</TableHead>
                  <TableHead>{{ $t('poDetail.table.status') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poDetail.table.openQty') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poDetail.table.receivedQty') }}</TableHead>
                  <TableHead class="text-right">{{ $t('poDetail.table.actions') }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow
                  v-for="line in order.lines"
                  :key="line.id"
                  class="group cursor-pointer hover:bg-accent/20"
                  @click="navigateToLine(line.id)"
                >
                  <TableCell class="font-medium">
                    {{ order.order_number }}-{{ line.line_number }}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" :class="getSupplierClasses(line.supplier_name)">
                      {{ line.supplier_name }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-muted-foreground">{{ line.item_code }}</TableCell>
                  <TableCell class="font-medium">{{ line.item_name }}</TableCell>
                  <TableCell class="text-muted-foreground">{{ line.order_date }}</TableCell>
                  <TableCell>{{ getLineNextCommitDate(line) }}</TableCell>
                  <TableCell>
                    <Badge variant="outline" :class="getStatusClasses(getLineStatus(line))">
                      {{ $t(`poManagement.status.${getLineStatus(line)}`) }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-right tabular-nums">
                    {{ formatNumber(getLineOpenQty(line)) }}
                  </TableCell>
                  <TableCell class="text-right tabular-nums">
                    {{ formatNumber(getLineReceivedQty(line)) }}
                  </TableCell>
                  <TableCell class="text-right">
                    <Button
                      variant="ghost"
                      size="xs"
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                      @click.stop="navigateToLine(line.id)"
                    >
                      <ExternalLink :size="14" data-icon="inline-start" />
                      {{ $t('poDetail.table.viewDetail') }}
                    </Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
