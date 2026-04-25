<script setup lang="ts">
  import type { HTMLAttributes } from 'vue'
  import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
  import {
    ChevronRight,
    ChevronDown,
    ChevronUp,
    ArrowUpDown,
    GripVertical,
    Maximize2,
    Minimize2,
  } from 'lucide-vue-next'
  import { cn } from '@/lib/utils'
  import { Checkbox } from '@/components/ui/checkbox'

  export interface DataTableColumn {
    key: string
    header: string
    width?: number
    minWidth?: number
    frozen?: boolean
    align?: 'left' | 'center' | 'right'
    editable?: boolean
    sortable?: boolean
  }

  const props = withDefaults(
    defineProps<{
      class?: HTMLAttributes['class']
      columns: DataTableColumn[]
      data: Record<string, unknown>[]
      rowKey?: string
      groupBy?: string
      loading?: boolean
      emptyText?: string
      searchable?: boolean
    }>(),
    { rowKey: 'id', emptyText: '沒有資料', searchable: false },
  )

  const emit = defineEmits<{
    'row-click': [row: Record<string, unknown>]
    'cell-update': [
      payload: { row: Record<string, unknown>; key: string; oldValue: unknown; newValue: string },
    ]
    'selection-change': [rows: Record<string, unknown>[]]
    'columns-reorder': [columns: DataTableColumn[]]
    'rows-reorder': [data: Record<string, unknown>[]]
  }>()

  const EXPAND_W = 36
  const DRAG_W = 28
  const CHECK_W = 36

  // ── Internal column order ────────────────────────────────────────────────────
  const internalColumns = ref<DataTableColumn[]>([])
  watch(
    () => props.columns,
    (cols) => {
      internalColumns.value = [...cols]
    },
    { immediate: true },
  )

  // ── Search ───────────────────────────────────────────────────────────────────
  const searchQuery = ref('')
  const searchedData = computed(() => {
    if (!searchQuery.value) return props.data
    const q = searchQuery.value.toLowerCase()
    return props.data.filter((row) =>
      internalColumns.value.some((col) =>
        String(row[col.key] ?? '')
          .toLowerCase()
          .includes(q),
      ),
    )
  })

  // ── Sort ─────────────────────────────────────────────────────────────────────
  const sortKey = ref<string | null>(null)
  const sortOrder = ref<'asc' | 'desc'>('asc')

  function toggleSort(col: DataTableColumn) {
    if (col.sortable === false) return
    if (sortKey.value === col.key) {
      if (sortOrder.value === 'asc') sortOrder.value = 'desc'
      else {
        sortKey.value = null
        sortOrder.value = 'asc'
      }
    } else {
      sortKey.value = col.key
      sortOrder.value = 'asc'
    }
  }

  const sortedData = computed(() => {
    const base = [...searchedData.value]
    if (!sortKey.value) return base
    const key = sortKey.value
    const dir = sortOrder.value === 'asc' ? 1 : -1
    return base.sort((a, b) => {
      const av = a[key],
        bv = b[key]
      if (av == null && bv == null) return 0
      if (av == null) return 1
      if (bv == null) return -1
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
      return String(av).localeCompare(String(bv)) * dir
    })
  })

  // ── Column widths & resize ───────────────────────────────────────────────────
  const colWidths = ref<Record<string, number>>({})
  onMounted(() => {
    for (const c of props.columns) colWidths.value[c.key] = c.width ?? 150
  })

  const resizeState = ref<{ key: string; startX: number; startW: number } | null>(null)

  function onResizeStart(e: MouseEvent, key: string) {
    e.preventDefault()
    e.stopPropagation()
    resizeState.value = { key, startX: e.clientX, startW: colWidths.value[key] }
    document.addEventListener('mousemove', onResizeMove)
    document.addEventListener('mouseup', onResizeEnd)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }
  function onResizeMove(e: MouseEvent) {
    if (!resizeState.value) return
    const { key, startX, startW } = resizeState.value
    const min = internalColumns.value.find((c) => c.key === key)?.minWidth ?? 50
    colWidths.value[key] = Math.max(min, startW + (e.clientX - startX))
  }
  function onResizeEnd() {
    resizeState.value = null
    document.removeEventListener('mousemove', onResizeMove)
    document.removeEventListener('mouseup', onResizeEnd)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
  onBeforeUnmount(() => {
    document.removeEventListener('mousemove', onResizeMove)
    document.removeEventListener('mouseup', onResizeEnd)
  })

  // ── Frozen offsets ───────────────────────────────────────────────────────────
  const fixedLeftBase = computed(() => DRAG_W + CHECK_W + EXPAND_W)

  const frozenLeftOffsets = computed(() => {
    const o: Record<string, number> = {}
    let cum = fixedLeftBase.value
    for (const c of internalColumns.value) {
      if (!c.frozen) break
      o[c.key] = cum
      cum += colWidths.value[c.key] ?? 150
    }
    return o
  })
  const frozenTotalW = computed(() => {
    let t = fixedLeftBase.value
    for (const c of internalColumns.value) {
      if (!c.frozen) break
      t += colWidths.value[c.key] ?? 150
    }
    return t
  })
  const hasFrozen = computed(() => internalColumns.value.some((c) => c.frozen))

  // ── Grouping ─────────────────────────────────────────────────────────────────
  const collapsedGroups = ref(new Set<string>())
  const groups = computed(() => {
    if (!props.groupBy) return [{ key: '__all__', rows: sortedData.value }]
    const m = new Map<string, Record<string, unknown>[]>()
    for (const r of sortedData.value) {
      const k = String(r[props.groupBy] ?? 'Other')
      if (!m.has(k)) m.set(k, [])
      m.get(k)!.push(r)
    }
    return Array.from(m, ([key, rows]) => ({ key, rows }))
  })
  function toggleGroup(k: string) {
    collapsedGroups.value.has(k) ? collapsedGroups.value.delete(k) : collapsedGroups.value.add(k)
  }

  // ── Expansion ────────────────────────────────────────────────────────────────
  const expandedRows = ref(new Set<unknown>())
  function toggleExpand(id: unknown) {
    expandedRows.value.has(id) ? expandedRows.value.delete(id) : expandedRows.value.add(id)
  }

  // ── Selection ────────────────────────────────────────────────────────────────
  const selectedKeys = ref(new Set<unknown>())
  const allSelected = computed(
    () =>
      sortedData.value.length > 0 &&
      sortedData.value.every((r) => selectedKeys.value.has(r[props.rowKey])),
  )
  const someSelected = computed(
    () =>
      sortedData.value.some((r) => selectedKeys.value.has(r[props.rowKey])) && !allSelected.value,
  )

  function toggleSelectAll() {
    if (allSelected.value) selectedKeys.value.clear()
    else sortedData.value.forEach((r) => selectedKeys.value.add(r[props.rowKey]))
    emitSelection()
  }
  function toggleSelectRow(id: unknown) {
    selectedKeys.value.has(id) ? selectedKeys.value.delete(id) : selectedKeys.value.add(id)
    emitSelection()
  }
  function emitSelection() {
    emit(
      'selection-change',
      sortedData.value.filter((r) => selectedKeys.value.has(r[props.rowKey])),
    )
  }

  // ── Focus ────────────────────────────────────────────────────────────────────
  const focusRow = ref(-1)
  const focusCol = ref(-1)
  const containerRef = ref<HTMLElement | null>(null)

  const flatRows = computed(() => {
    const res: Record<string, unknown>[] = []
    for (const g of groups.value) {
      if (props.groupBy && collapsedGroups.value.has(g.key)) continue
      res.push(...g.rows)
    }
    return res
  })
  function rowIdx(row: Record<string, unknown>) {
    return flatRows.value.indexOf(row)
  }
  function onCellClick(row: Record<string, unknown>, ci: number) {
    focusRow.value = rowIdx(row)
    focusCol.value = ci
    containerRef.value?.focus()
    if (
      editingCell.value &&
      (editingCell.value.row !== focusRow.value || editingCell.value.col !== ci)
    )
      cancelEdit()
  }

  // ── Inline editing ───────────────────────────────────────────────────────────
  const editingCell = ref<{ row: number; col: number } | null>(null)
  const editValue = ref('')
  const editInputRef = ref<HTMLInputElement | null>(null)

  function startEdit(r?: number, c?: number) {
    const ri = r ?? focusRow.value,
      ci = c ?? focusCol.value
    if (ri < 0 || ci < 0) return
    const col = internalColumns.value[ci]
    if (!col?.editable) return
    const row = flatRows.value[ri]
    if (!row) return
    editingCell.value = { row: ri, col: ci }
    editValue.value = String(row[col.key] ?? '')
    nextTick(() => {
      editInputRef.value?.focus()
      editInputRef.value?.select()
    })
  }
  function commitEdit() {
    if (!editingCell.value) return
    const { row: ri, col: ci } = editingCell.value
    const col = internalColumns.value[ci],
      row = flatRows.value[ri]
    if (row && col) {
      const old = row[col.key]
      if (String(old) !== editValue.value)
        emit('cell-update', { row, key: col.key, oldValue: old, newValue: editValue.value })
    }
    editingCell.value = null
  }
  function cancelEdit() {
    editingCell.value = null
  }
  function onEditKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault()
      commitEdit()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      cancelEdit()
    } else if (e.key === 'Tab') {
      e.preventDefault()
      commitEdit()
      const nc = focusCol.value + (e.shiftKey ? -1 : 1)
      if (nc >= 0 && nc < internalColumns.value.length) {
        focusCol.value = nc
        if (internalColumns.value[nc].editable) nextTick(() => startEdit())
      }
    }
  }

  // ── Copy ─────────────────────────────────────────────────────────────────────
  function handleCopy() {
    if (focusRow.value < 0 || focusCol.value < 0 || editingCell.value) return
    const row = flatRows.value[focusRow.value],
      col = internalColumns.value[focusCol.value]
    if (row && col) navigator.clipboard.writeText(String(row[col.key] ?? '')).catch(() => {})
  }

  // ── Keyboard nav ─────────────────────────────────────────────────────────────
  function onKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
      handleCopy()
      return
    }
    if (editingCell.value) return
    const total = flatRows.value.length,
      cols = internalColumns.value.length
    if (total === 0) return
    if (focusRow.value < 0) focusRow.value = 0
    if (focusCol.value < 0) focusCol.value = 0
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        focusRow.value = Math.min(focusRow.value + 1, total - 1)
        scrollIntoView()
        break
      case 'ArrowUp':
        e.preventDefault()
        focusRow.value = Math.max(focusRow.value - 1, 0)
        scrollIntoView()
        break
      case 'ArrowRight':
        e.preventDefault()
        focusCol.value = Math.min(focusCol.value + 1, cols - 1)
        break
      case 'ArrowLeft':
        e.preventDefault()
        focusCol.value = Math.max(focusCol.value - 1, 0)
        break
      case 'Enter':
      case 'F2':
        e.preventDefault()
        if (internalColumns.value[focusCol.value]?.editable) startEdit()
        else if (e.key === 'Enter') {
          const r = flatRows.value[focusRow.value]
          if (r) toggleExpand(r[props.rowKey])
        }
        break
      case 'Escape':
        focusRow.value = -1
        focusCol.value = -1
        break
      case ' ':
        if (focusRow.value >= 0) {
          e.preventDefault()
          toggleSelectRow(flatRows.value[focusRow.value]?.[props.rowKey])
        }
        break
      default:
        if (
          e.key.length === 1 &&
          !e.ctrlKey &&
          !e.metaKey &&
          !e.altKey &&
          internalColumns.value[focusCol.value]?.editable
        ) {
          editValue.value = ''
          startEdit()
        }
        break
    }
  }
  function scrollIntoView() {
    nextTick(() => {
      containerRef.value
        ?.querySelector('[data-focus]')
        ?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
    })
  }

  // ── Column drag reorder ──────────────────────────────────────────────────────
  const dragColIdx = ref(-1)
  const dragOverColIdx = ref(-1)

  function onColDragStart(e: DragEvent, idx: number) {
    if (internalColumns.value[idx].frozen) {
      e.preventDefault()
      return
    }
    dragColIdx.value = idx
    e.dataTransfer!.effectAllowed = 'move'
  }
  function onColDragOver(e: DragEvent, idx: number) {
    e.preventDefault()
    if (internalColumns.value[idx].frozen) return
    dragOverColIdx.value = idx
  }
  function onColDrop(e: DragEvent, idx: number) {
    e.preventDefault()
    if (dragColIdx.value < 0 || internalColumns.value[idx].frozen) return
    const cols = [...internalColumns.value]
    const [moved] = cols.splice(dragColIdx.value, 1)
    cols.splice(idx, 0, moved)
    internalColumns.value = cols
    emit('columns-reorder', cols)
    dragColIdx.value = -1
    dragOverColIdx.value = -1
  }
  function onColDragEnd() {
    dragColIdx.value = -1
    dragOverColIdx.value = -1
  }

  // ── Row drag reorder ─────────────────────────────────────────────────────────
  const dragRowIdx = ref(-1)
  const dragOverRowIdx = ref(-1)

  function onRowDragStart(e: DragEvent, idx: number) {
    dragRowIdx.value = idx
    e.dataTransfer!.effectAllowed = 'move'
  }
  function onRowDragOver(e: DragEvent, idx: number) {
    e.preventDefault()
    dragOverRowIdx.value = idx
  }
  function onRowDrop(e: DragEvent, idx: number) {
    e.preventDefault()
    if (dragRowIdx.value < 0) return
    const d = [...props.data]
    const fromRow = flatRows.value[dragRowIdx.value]
    const toRow = flatRows.value[idx]
    const fi = d.indexOf(fromRow),
      ti = d.indexOf(toRow)
    if (fi >= 0 && ti >= 0) {
      d.splice(fi, 1)
      d.splice(ti, 0, fromRow)
      emit('rows-reorder', d)
    }
    dragRowIdx.value = -1
    dragOverRowIdx.value = -1
  }
  function onRowDragEnd() {
    dragRowIdx.value = -1
    dragOverRowIdx.value = -1
  }

  // ── Cell style ───────────────────────────────────────────────────────────────
  function cellSt(col: DataTableColumn): Record<string, string> {
    const w = colWidths.value[col.key] ?? 150
    const s: Record<string, string> = { width: `${w}px`, minWidth: `${w}px`, maxWidth: `${w}px` }
    if (col.frozen && col.key in frozenLeftOffsets.value) {
      s.position = 'sticky'
      s.left = `${frozenLeftOffsets.value[col.key]}px`
    }
    return s
  }
</script>

<template>
  <div class="space-y-2">
    <!-- Search bar -->
    <div v-if="searchable" class="relative max-w-xs">
      <input
        v-model="searchQuery"
        placeholder="搜尋表格..."
        class="h-8 w-full rounded-md border border-input bg-transparent px-3 text-sm outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-ring/50 focus:ring-[3px]"
      />
    </div>

    <!-- Table container -->
    <div
      ref="containerRef"
      :class="
        cn(
          'adt relative overflow-auto rounded-md border bg-background focus:outline-none',
          props.class,
        )
      "
      style="max-height: 600px"
      tabindex="0"
      @keydown="onKeydown"
    >
      <table class="w-max min-w-full border-collapse" style="table-layout: fixed">
        <thead class="sticky top-0 z-30">
          <tr>
            <!-- Drag handle col -->
            <th
              class="sticky left-0 z-40 h-10 border-b bg-muted/80 backdrop-blur"
              :style="{ width: DRAG_W + 'px', minWidth: DRAG_W + 'px' }"
            />
            <!-- Checkbox col -->
            <th
              class="sticky z-40 h-10 border-b bg-muted/80 px-1 text-center backdrop-blur"
              :style="{ left: DRAG_W + 'px', width: CHECK_W + 'px', minWidth: CHECK_W + 'px' }"
            >
              <Checkbox
                :checked="allSelected ? true : someSelected ? 'indeterminate' : false"
                class="mx-auto"
                @update:checked="toggleSelectAll"
              />
            </th>
            <!-- Expand col -->
            <th
              class="sticky z-40 h-10 border-b bg-muted/80 backdrop-blur"
              :style="{
                left: DRAG_W + CHECK_W + 'px',
                width: EXPAND_W + 'px',
                minWidth: EXPAND_W + 'px',
              }"
            />
            <!-- Data columns -->
            <th
              v-for="(col, ci) in internalColumns"
              :key="col.key"
              :style="cellSt(col)"
              :draggable="!col.frozen"
              :class="
                cn(
                  'group/th relative h-10 border-b bg-muted/80 px-3 text-left text-xs font-medium tracking-wide text-muted-foreground backdrop-blur select-none',
                  col.frozen && 'z-40',
                  col.align === 'center' && 'text-center',
                  col.align === 'right' && 'text-right',
                  dragOverColIdx === ci && dragColIdx !== ci && 'border-l-2 border-l-primary',
                )
              "
              @dragstart="onColDragStart($event, ci)"
              @dragover="onColDragOver($event, ci)"
              @drop="onColDrop($event, ci)"
              @dragend="onColDragEnd"
            >
              <button
                class="inline-flex items-center gap-1 truncate font-medium transition-colors hover:text-foreground"
                @click="toggleSort(col)"
              >
                <span class="truncate">{{ col.header }}</span>
                <ChevronUp
                  v-if="sortKey === col.key && sortOrder === 'asc'"
                  class="h-3 w-3 shrink-0 text-foreground"
                />
                <ChevronDown
                  v-else-if="sortKey === col.key && sortOrder === 'desc'"
                  class="h-3 w-3 shrink-0 text-foreground"
                />
                <ArrowUpDown
                  v-else-if="col.sortable !== false"
                  class="h-3 w-3 shrink-0 opacity-0 transition-opacity group-hover/th:opacity-40"
                />
              </button>
              <!-- Resize handle -->
              <div
                class="absolute -right-[3px] top-0 z-50 flex h-full w-[7px] cursor-col-resize items-center justify-center opacity-0 transition-opacity hover:opacity-100 group-hover/th:opacity-60"
                @mousedown="onResizeStart($event, col.key)"
              >
                <div class="h-4 w-[3px] rounded-full bg-primary/60" />
              </div>
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Loading -->
          <template v-if="loading">
            <tr v-for="i in 5" :key="i" class="border-b">
              <td :colspan="internalColumns.length + 3" class="px-4 py-3">
                <div class="h-4 animate-pulse rounded bg-muted" />
              </td>
            </tr>
          </template>

          <!-- Empty -->
          <tr v-else-if="sortedData.length === 0">
            <td
              :colspan="internalColumns.length + 3"
              class="py-10 text-center text-sm text-muted-foreground"
            >
              {{ emptyText }}
            </td>
          </tr>

          <!-- Data -->
          <template v-else>
            <template v-for="group in groups" :key="group.key">
              <!-- Group header -->
              <tr v-if="groupBy" class="border-b bg-muted/30">
                <td :colspan="internalColumns.length + 3" class="px-4 py-1.5">
                  <button
                    class="flex items-center gap-1.5 text-xs font-semibold text-foreground/80"
                    @click="toggleGroup(group.key)"
                  >
                    <component
                      :is="collapsedGroups.has(group.key) ? ChevronRight : ChevronDown"
                      class="h-3.5 w-3.5"
                    />
                    {{ group.key }}
                    <span class="font-normal text-muted-foreground">({{ group.rows.length }})</span>
                  </button>
                </td>
              </tr>

              <template v-if="!groupBy || !collapsedGroups.has(group.key)">
                <template v-for="(row, ri) in group.rows" :key="row[rowKey]">
                  <tr
                    :class="
                      cn(
                        'group border-b transition-colors',
                        selectedKeys.has(row[rowKey]) && 'bg-primary/5',
                        rowIdx(row) === focusRow &&
                          !selectedKeys.has(row[rowKey]) &&
                          'bg-accent/10',
                        'hover:bg-muted/40',
                        dragOverRowIdx === rowIdx(row) &&
                          dragRowIdx !== rowIdx(row) &&
                          'border-t-2 border-t-primary',
                      )
                    "
                    @click="emit('row-click', row)"
                    @dragover="onRowDragOver($event, rowIdx(row))"
                    @drop="onRowDrop($event, rowIdx(row))"
                  >
                    <!-- Drag handle -->
                    <td
                      class="sticky left-0 z-[1] bg-background px-0.5 text-center transition-colors group-hover:bg-muted/40"
                      :style="{ width: DRAG_W + 'px', minWidth: DRAG_W + 'px' }"
                      draggable="true"
                      @dragstart="onRowDragStart($event, rowIdx(row))"
                      @dragend="onRowDragEnd"
                    >
                      <GripVertical
                        class="mx-auto h-3.5 w-3.5 cursor-grab text-muted-foreground/40 opacity-0 transition-opacity group-hover:opacity-100"
                      />
                    </td>
                    <!-- Checkbox -->
                    <td
                      class="sticky z-[1] bg-background px-1 text-center transition-colors group-hover:bg-muted/40"
                      :style="{
                        left: DRAG_W + 'px',
                        width: CHECK_W + 'px',
                        minWidth: CHECK_W + 'px',
                      }"
                    >
                      <Checkbox
                        :checked="selectedKeys.has(row[rowKey])"
                        class="mx-auto"
                        @update:checked="toggleSelectRow(row[rowKey])"
                        @click.stop
                      />
                    </td>
                    <!-- Expand -->
                    <td
                      class="sticky z-[1] bg-background px-1 text-center transition-colors group-hover:bg-muted/40"
                      :style="{
                        left: DRAG_W + CHECK_W + 'px',
                        width: EXPAND_W + 'px',
                        minWidth: EXPAND_W + 'px',
                      }"
                    >
                      <button
                        class="inline-flex h-5 w-5 items-center justify-center rounded text-muted-foreground/50 hover:text-foreground"
                        @click.stop="toggleExpand(row[rowKey])"
                      >
                        <component
                          :is="expandedRows.has(row[rowKey]) ? Minimize2 : Maximize2"
                          class="h-3 w-3"
                        />
                      </button>
                    </td>
                    <!-- Data cells -->
                    <td
                      v-for="(col, ci) in internalColumns"
                      :key="col.key"
                      :style="cellSt(col)"
                      :data-focus="rowIdx(row) === focusRow && focusCol === ci ? '' : undefined"
                      :class="
                        cn(
                          'relative px-3 py-2 text-sm transition-colors',
                          col.frozen && 'z-[1] bg-background group-hover:bg-muted/40',
                          col.align === 'center' && 'text-center',
                          col.align === 'right' && 'text-right tabular-nums',
                          rowIdx(row) === focusRow &&
                            focusCol === ci &&
                            'ring-2 ring-inset ring-primary/60',
                        )
                      "
                      @click.stop="onCellClick(row, ci)"
                      @dblclick.stop="startEdit(rowIdx(row), ci)"
                    >
                      <input
                        v-if="
                          editingCell && editingCell.row === rowIdx(row) && editingCell.col === ci
                        "
                        ref="editInputRef"
                        v-model="editValue"
                        class="absolute inset-0 z-10 w-full border-2 border-primary bg-background px-3 text-sm outline-none"
                        @blur="commitEdit"
                        @keydown="onEditKeydown"
                      />
                      <template v-else>
                        <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                          <span class="block truncate">{{ row[col.key] }}</span>
                        </slot>
                      </template>
                    </td>
                  </tr>
                  <!-- Expanded -->
                  <tr v-if="expandedRows.has(row[rowKey])" class="border-b bg-muted/10">
                    <td :colspan="internalColumns.length + 3" class="p-4">
                      <slot name="expanded-row" :row="row">
                        <pre class="text-xs text-foreground/70">{{
                          JSON.stringify(row, null, 2)
                        }}</pre>
                      </slot>
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </template>
        </tbody>
      </table>

      <!-- Frozen shadow -->
      <div
        v-if="hasFrozen"
        class="pointer-events-none absolute inset-y-0 z-20"
        :style="{
          left: frozenTotalW + 'px',
          width: '4px',
          background: 'linear-gradient(to right, hsl(var(--border)/0.25), transparent)',
        }"
      />
    </div>

    <!-- Selection count -->
    <div v-if="selectedKeys.size > 0" class="text-xs text-muted-foreground">
      已選取 {{ selectedKeys.size }} 筆
    </div>
  </div>
</template>

<style scoped>
  .adt th {
    position: relative;
  }
  .adt ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  .adt ::-webkit-scrollbar-thumb {
    background: hsl(var(--border) / 0.4);
    border-radius: 10px;
  }
  .adt ::-webkit-scrollbar-thumb:hover {
    background: hsl(var(--border) / 0.7);
  }
</style>
