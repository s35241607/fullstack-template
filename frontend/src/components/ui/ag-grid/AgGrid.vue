<script setup lang="ts">
  import { AgGridVue } from 'ag-grid-vue3'
  import {
    ModuleRegistry,
    AllCommunityModule,
    themeQuartz,
    type CellFocusedEvent,
    type CellKeyDownEvent,
    type CellMouseDownEvent,
    type CellMouseOverEvent,
    type CellValueChangedEvent,
    type ColDef,
    type Column,
    type GridApi,
    type GridOptions,
    type GridReadyEvent,
    type IRowNode,
    type SuppressPasteCallbackParams,
    type Theme,
    type ValueParserParams,
  } from 'ag-grid-community'
  import { computed, ref, onUnmounted, nextTick, watch } from 'vue'
  import { useDark } from '@vueuse/core'

  // Register all required community modules
  ModuleRegistry.registerModules([AllCommunityModule])

  type GridRowData = Record<string, unknown>
  type GridColumnDef = ColDef<GridRowData>
  type CellPoint = { rowIndex: number; colId: string }
  type CellRange = { start: CellPoint; end: CellPoint }
  type ClipboardMatrix = string[][]

  interface Props {
    rowData: GridRowData[]
    columnDefs: GridColumnDef[]
    height?: string | number
    gridOptions?: GridOptions<GridRowData>
  }

  withDefaults(defineProps<Props>(), {
    height: '500px',
    gridOptions: () => ({}),
  })

  const isDark = useDark()

  /**
   * AG Grid v35 Theming API (official approach):
   *
   * themeQuartz uses `colorSchemeVariable` by default.
   * It reacts to `data-ag-theme-mode` attribute on any parent element.
   * We set this attribute on the wrapper div and toggle it reactively.
   *
   * Ref: https://www.ag-grid.com/vue-data-grid/theming-colors/#theme-modes
   */
  const gridTheme = computed<Theme>(() => {
    return themeQuartz.withParams({
      borderRadius: 6,
      headerHeight: 38,
      rowHeight: 36,
      fontSize: 14,
      fontFamily: 'inherit', // Follows the parent application font
      backgroundColor: isDark.value ? '#09090b' : '#ffffff',
      foregroundColor: isDark.value ? '#fafafa' : '#09090b',
      headerBackgroundColor: isDark.value ? '#09090b' : '#f9fafb',
      headerTextColor: isDark.value ? '#a1a1aa' : '#71717a',
      borderColor: isDark.value ? '#27272a' : '#e4e4e7',
    })
  })

  const themeMode = computed(() => (isDark.value ? 'dark' : 'light'))

  const gridContainer = ref<HTMLElement | null>(null)
  const gridApi = ref<GridApi<GridRowData> | null>(null)
  const isSelecting = ref(false)
  const selectedRanges = ref<CellRange[]>([])
  const currentRangeIndex = ref(-1)
  const gridReady = ref(false)

  // ResizeObserver — 宣告在模組層級，以便 onUnmounted 中清除（避免記憶體洩漏）
  let resizeObserver: ResizeObserver | null = null

  // Fill handle state
  type FillHandlePos = { left: number; top: number }
  type FillRect = { left: number; top: number; width: number; height: number }
  const fillHandlePos = ref<FillHandlePos | null>(null)
  const fillDragging = ref(false)
  const fillSourceRange = ref<CellRange | null>(null)
  const fillPreviewRange = ref<CellRange | null>(null)
  const fillPreviewRect = ref<FillRect | null>(null)
  const selectionRects = ref<FillRect[]>([])
  const copyRanges = ref<CellRange[]>([])
  const copyRects = ref<FillRect[]>([])

  // ─── Undo Stack ───────────────────────────────────────────────────────────────

  type UndoEntry = { rowIndex: number; colId: string; oldValue: unknown; newValue: unknown }[]
  const undoStack: UndoEntry[] = []
  const redoStack: UndoEntry[] = []
  const MAX_UNDO_STEPS = 100

  const pushUndo = (entries: UndoEntry) => {
    if (entries.length === 0) return
    undoStack.push(entries)
    redoStack.length = 0 // Clear redo stack on new action
    if (undoStack.length > MAX_UNDO_STEPS) undoStack.shift()
  }

  const applyUndo = () => {
    const api = gridApi.value
    if (!api || undoStack.length === 0) return

    const entries = undoStack.pop()!
    redoStack.push(entries)

    const displayedColumns = getDisplayedColumns()
    const colMap = new Map(displayedColumns.map((c) => [c.getColId(), c]))

    api.stopEditing()

    for (const { rowIndex, colId, oldValue } of entries) {
      const rowNode = api.getDisplayedRowAtIndex(rowIndex)
      const column = colMap.get(colId)
      if (!rowNode || !column) continue
      rowNode.setDataValue(column, oldValue, 'undo')
    }

    // 必須強制重繪，否則 cellClassRules 不會重新評估，視覺上看起來像是沒有反應
    api.refreshCells({ force: true })
  }

  const applyRedo = () => {
    const api = gridApi.value
    if (!api || redoStack.length === 0) return

    const entries = redoStack.pop()!
    undoStack.push(entries)

    const displayedColumns = getDisplayedColumns()
    const colMap = new Map(displayedColumns.map((c) => [c.getColId(), c]))

    api.stopEditing()

    for (const { rowIndex, colId, newValue } of entries) {
      const rowNode = api.getDisplayedRowAtIndex(rowIndex)
      const column = colMap.get(colId)
      if (!rowNode || !column) continue
      rowNode.setDataValue(column, newValue, 'redo')
    }

    api.refreshCells({ force: true })
  }

  const getDisplayedColumns = (): Column[] => {
    return gridApi.value?.getAllDisplayedColumns() ?? []
  }

  const getPinnedLeftWidth = (): number => {
    const api = gridApi.value
    if (!api) return 0
    return api
      .getAllDisplayedColumns()
      .filter((c) => c.getPinned() === 'left')
      .reduce((acc, c) => acc + c.getActualWidth(), 0)
  }

  const getPinnedRightWidth = (): number => {
    const api = gridApi.value
    if (!api) return 0
    return api
      .getAllDisplayedColumns()
      .filter((c) => c.getPinned() === 'right')
      .reduce((acc, c) => acc + c.getActualWidth(), 0)
  }

  const getColumnIds = (): string[] => {
    return getDisplayedColumns().map((column) => column.getColId())
  }

  const getCellId = (point: CellPoint): string => {
    return `${point.rowIndex}:${point.colId}`
  }

  const getNormalizedRange = (range: CellRange) => {
    const columnIds = getColumnIds()
    const startColumnIndex = columnIds.indexOf(range.start.colId)
    const endColumnIndex = columnIds.indexOf(range.end.colId)

    if (startColumnIndex === -1 || endColumnIndex === -1) {
      return null
    }

    const rowStart = Math.min(range.start.rowIndex, range.end.rowIndex)
    const rowEnd = Math.max(range.start.rowIndex, range.end.rowIndex)
    const colStart = Math.min(startColumnIndex, endColumnIndex)
    const colEnd = Math.max(startColumnIndex, endColumnIndex)

    return {
      rowStart,
      rowEnd,
      colStart,
      colEnd,
      columnIds: columnIds.slice(colStart, colEnd + 1),
    }
  }

  const isPointInRange = (point: CellPoint, range: CellRange): boolean => {
    const normalized = getNormalizedRange(range)
    if (!normalized) return false

    const colIdx = getColumnIds().indexOf(point.colId)
    return (
      point.rowIndex >= normalized.rowStart &&
      point.rowIndex <= normalized.rowEnd &&
      colIdx >= normalized.colStart &&
      colIdx <= normalized.colEnd
    )
  }

  const isCellSelected = (rowIndex: number, colId: string): boolean => {
    const point = { rowIndex, colId }
    return selectedRanges.value.some((range) => isPointInRange(point, range))
  }

  const focusCell = async (point: CellPoint) => {
    const api = gridApi.value
    const column = getDisplayedColumns().find((item) => item.getColId() === point.colId)

    if (!api || !column) {
      return
    }

    _suppressFocusSync = true
    api.ensureIndexVisible(point.rowIndex)
    api.ensureColumnVisible(column)
    api.setFocusedCell(point.rowIndex, column)
    // AG Grid 的 cellFocused 事件在 microtask 中觸發，需等待 nextTick 後再清除 flag
    // 否則 onCellFocused 會在 flag=false 時執行，導致多格選取被重置為單格
    await nextTick()
    _suppressFocusSync = false
  }

  const getFocusedPoint = (): CellPoint | null => {
    const focusedCell = gridApi.value?.getFocusedCell()

    if (!focusedCell || focusedCell.rowIndex === null || focusedCell.rowPinned) {
      return null
    }

    return {
      rowIndex: focusedCell.rowIndex,
      colId: focusedCell.column.getColId(),
    }
  }

  // ─── Fill Handle: Positioning ────────────────────────────────────────────────

  const getBottomRightCellElement = (range: CellRange): HTMLElement | null => {
    const container = gridContainer.value
    const normalizedRange = getNormalizedRange(range)

    if (!container || !normalizedRange) return null

    const rowIndex = normalizedRange.rowEnd
    const colId = normalizedRange.columnIds[normalizedRange.columnIds.length - 1]

    // AG Grid renders cells with these attributes on the cell element
    return container.querySelector<HTMLElement>(`[row-index="${rowIndex}"] [col-id="${colId}"]`)
  }

  const updateFillHandlePosition = async () => {
    if (selectedRanges.value.length === 0) {
      fillHandlePos.value = null
      return
    }

    // Don't update while user is dragging to select (prevents flickering)
    if (isSelecting.value) return
    // Use requestAnimationFrame to ensure AG Grid has finished rendering
    requestAnimationFrame(() => {
      const container = gridContainer.value
      const lastRange = selectedRanges.value[selectedRanges.value.length - 1]
      const cellEl = getBottomRightCellElement(lastRange)

      if (!container || !cellEl) {
        fillHandlePos.value = null
        return
      }

      const containerRect = container.getBoundingClientRect()
      const cellRect = cellEl.getBoundingClientRect()

      fillHandlePos.value = {
        left: cellRect.right - containerRect.left,
        top: cellRect.bottom - containerRect.top,
      }
    })
  }

  const updateAllRects = () => {
    requestAnimationFrame(() => {
      updateSelectionRects()
      updateCopyRects()
      updateFillHandlePosition()
      if (fillDragging.value) updateFillPreviewRect()
    })
  }

  // Watch selectedRanges for changes to update fill handle position
  watch(selectedRanges, updateFillHandlePosition, { deep: true })

  // ─── Fill Handle: Scroll tracking ────────────────────────────────────────────

  let scrollViewport: Element | null = null

  // RAF ID for scroll handler throttling
  let _scrollRafId: number | null = null

  // AG Grid 原生的 @body-scroll 事件（包含溭動區與凍結欄滝動）
  // 用 requestAnimationFrame 節流，防止滚動時 layout thrashing
  const onBodyScroll = () => {
    if (_scrollRafId !== null) cancelAnimationFrame(_scrollRafId)
    _scrollRafId = requestAnimationFrame(() => {
      updateAllRects()
      _scrollRafId = null
    })
  }

  // onBodyViewportScroll 已不需要（改由 AG Grid @body-scroll 統一處理）
  // 保留時需外部事件符讙使用
  const onBodyViewportScroll = () => onBodyScroll()

  // ─── Range & Copy Overlays ───────────────────────────────────────────────────

  /**
   * Synchronously compute the bounding rect of a cell range relative to gridContainer.
   * No nextTick needed — cell positions don't change when selection state changes.
   */
  const computeRangeRect = (range: CellRange): FillRect | null => {
    const container = gridContainer.value
    const normalizedRange = getNormalizedRange(range)
    if (!container || !normalizedRange) return null

    const containerRect = container.getBoundingClientRect()
    const firstColId = normalizedRange.columnIds[0]
    const lastColId = normalizedRange.columnIds[normalizedRange.columnIds.length - 1]

    const topLeftEl = container.querySelector<HTMLElement>(
      `[row-index="${normalizedRange.rowStart}"] [col-id="${firstColId}"]`,
    )
    const bottomRightEl = container.querySelector<HTMLElement>(
      `[row-index="${normalizedRange.rowEnd}"] [col-id="${lastColId}"]`,
    )

    if (!topLeftEl || !bottomRightEl) return null

    const tlRect = topLeftEl.getBoundingClientRect()
    const brRect = bottomRightEl.getBoundingClientRect()

    return {
      left: tlRect.left - containerRect.left,
      top: tlRect.top - containerRect.top,
      width: brRect.right - tlRect.left,
      height: brRect.bottom - tlRect.top,
    }
  }

  const updateSelectionRects = () => {
    // Don't render an overlay for a plain single-cell selection — the
    // `.ag-cell-focus` CSS border already handles that case. Only show the
    // overlay when multiple cells or multiple ranges are selected.
    const needsOverlay = (range: CellRange): boolean => {
      if (selectedRanges.value.length > 1) return true
      return range.start.rowIndex !== range.end.rowIndex || range.start.colId !== range.end.colId
    }
    selectionRects.value = selectedRanges.value
      .filter(needsOverlay)
      .map((range) => computeRangeRect(range))
      .filter((rect): rect is FillRect => rect !== null)
  }

  const updateCopyRects = () => {
    copyRects.value = copyRanges.value
      .map((range) => computeRangeRect(range))
      .filter((rect): rect is FillRect => rect !== null)
  }

  const clearCopyState = () => {
    copyRanges.value = []
    copyRects.value = []
  }

  // ─── Fill Handle: Drag Logic ─────────────────────────────────────────────────

  const getCellAtPoint = (x: number, y: number): CellPoint | null => {
    const elements = document.elementsFromPoint(x, y)

    for (const el of elements) {
      if (!(el instanceof HTMLElement)) continue

      // Look for an AG Grid cell element
      const cellEl =
        el.closest<HTMLElement>('[col-id][row-index]') ?? el.closest<HTMLElement>('[col-id]')

      if (!cellEl) continue

      const colId = cellEl.getAttribute('col-id')

      // Try to get row-index from the cell or its parent row element
      const rowEl = cellEl.closest<HTMLElement>('[row-index]')
      const rowIndexAttr = rowEl?.getAttribute('row-index')

      if (!colId || !rowIndexAttr || rowIndexAttr === 'undefined') continue

      const rowIndex = parseInt(rowIndexAttr, 10)
      if (Number.isNaN(rowIndex) || rowIndex < 0) continue

      return { rowIndex, colId }
    }

    return null
  }

  const computeFillExtendedRange = (source: CellRange, target: CellPoint): CellRange | null => {
    const normalizedSource = getNormalizedRange(source)
    if (!normalizedSource) return null

    const { rowStart, rowEnd, columnIds } = normalizedSource
    const columnIdsList = getColumnIds()
    const sourceColStart = columnIdsList.indexOf(columnIds[0])
    const sourceColEnd = columnIdsList.indexOf(columnIds[columnIds.length - 1])

    const rowDelta =
      target.rowIndex < rowStart
        ? target.rowIndex - rowStart
        : target.rowIndex > rowEnd
          ? target.rowIndex - rowEnd
          : 0

    const targetColIdx = columnIdsList.indexOf(target.colId)
    const colDelta =
      targetColIdx < sourceColStart
        ? targetColIdx - sourceColStart
        : targetColIdx > sourceColEnd
          ? targetColIdx - sourceColEnd
          : 0

    if (rowDelta === 0 && colDelta === 0) return null

    const absRow = Math.abs(rowDelta)
    const absCol = Math.abs(colDelta)

    // Extend only in the dominant axis direction
    if (absRow >= absCol) {
      // Vertical fill
      if (rowDelta > 0) {
        return {
          start: { rowIndex: rowStart, colId: columnIds[0] },
          end: { rowIndex: target.rowIndex, colId: columnIds[columnIds.length - 1] },
        }
      } else {
        return {
          start: { rowIndex: target.rowIndex, colId: columnIds[0] },
          end: { rowIndex: rowEnd, colId: columnIds[columnIds.length - 1] },
        }
      }
    } else {
      // Horizontal fill
      if (colDelta > 0) {
        return {
          start: { rowIndex: rowStart, colId: columnIds[0] },
          end: { rowIndex: rowEnd, colId: target.colId },
        }
      } else {
        return {
          start: { rowIndex: rowStart, colId: target.colId },
          end: { rowIndex: rowEnd, colId: columnIds[columnIds.length - 1] },
        }
      }
    }
  }

  const updateFillPreviewRect = () => {
    fillPreviewRect.value = fillPreviewRange.value ? computeRangeRect(fillPreviewRange.value) : null
  }

  const handleFillDragMove = (event: MouseEvent) => {
    if (!fillDragging.value || !fillSourceRange.value) return

    const target = getCellAtPoint(event.clientX, event.clientY)
    if (!target) return

    const extended = computeFillExtendedRange(fillSourceRange.value, target)
    fillPreviewRange.value = extended
    updateFillPreviewRect()
  }

  const onFillHandleMouseDown = (event: MouseEvent) => {
    if (event.button !== 0) return
    event.preventDefault()
    event.stopPropagation()

    const lastRange = selectedRanges.value[selectedRanges.value.length - 1]
    if (!lastRange) return

    fillSourceRange.value = {
      start: { ...lastRange.start },
      end: { ...lastRange.end },
    }
    fillDragging.value = true
    fillPreviewRange.value = null
    fillPreviewRect.value = null
  }

  // ─── Fill Handle: Apply Fill ─────────────────────────────────────────────────

  const getRangeValues = (range: CellRange): string[][] => {
    const api = gridApi.value
    const normalizedRange = getNormalizedRange(range)
    if (!api || !normalizedRange) return []

    const displayedColumns = getDisplayedColumns()
    const matrix: string[][] = []

    for (let rowIndex = normalizedRange.rowStart; rowIndex <= normalizedRange.rowEnd; rowIndex++) {
      const rowNode = api.getDisplayedRowAtIndex(rowIndex)
      const row = normalizedRange.columnIds.map((colId) => {
        const column = displayedColumns.find((c) => c.getColId() === colId)
        if (!rowNode || !column) return ''
        const value = getCellRawValue(rowNode, column)
        return formatClipboardValue({ rowNode, column, value })
      })
      matrix.push(row)
    }

    return matrix
  }

  const applyFill = () => {
    const api = gridApi.value
    const source = fillSourceRange.value
    const preview = fillPreviewRange.value

    if (!api || !source || !preview) return

    const normalizedSource = getNormalizedRange(source)
    const normalizedPreview = getNormalizedRange(preview)

    if (!normalizedSource || !normalizedPreview) return

    const sourceMatrix = getRangeValues(source)
    const displayedColumns = getDisplayedColumns()
    const colMap = new Map(displayedColumns.map((c) => [c.getColId(), c]))

    api.stopEditing()

    const undoEntries: UndoEntry = []

    for (
      let rowIndex = normalizedPreview.rowStart;
      rowIndex <= normalizedPreview.rowEnd;
      rowIndex++
    ) {
      const rowNode = api.getDisplayedRowAtIndex(rowIndex)
      if (!rowNode) continue

      // Source row to repeat (tile pattern from source)
      const sourceRowOffset = (rowIndex - normalizedPreview.rowStart) % sourceMatrix.length
      const sourceRow = sourceMatrix[sourceRowOffset]

      for (let colIdx = 0; colIdx < normalizedPreview.columnIds.length; colIdx++) {
        const colId = normalizedPreview.columnIds[colIdx]
        const column = colMap.get(colId)
        if (!column || !canPasteIntoCell(rowNode, column)) continue

        const sourceColOffset = colIdx % (sourceRow?.length ?? 1)
        const rawValue = sourceRow?.[sourceColOffset] ?? ''
        const newValue = parsePastedValue(rowNode, column, rawValue)
        undoEntries.push({
          rowIndex,
          colId,
          oldValue: getCellRawValue(rowNode, column),
          newValue,
        })
        rowNode.setDataValue(column, newValue, 'fill')
      }
    }

    pushUndo(undoEntries)

    // Update selection to cover the full filled area (source + fill area)
    const allRowStart = Math.min(normalizedSource.rowStart, normalizedPreview.rowStart)
    const allRowEnd = Math.max(normalizedSource.rowEnd, normalizedPreview.rowEnd)
    const allColStart = Math.min(normalizedSource.colStart, normalizedPreview.colStart)
    const allColEnd = Math.max(normalizedSource.colEnd, normalizedPreview.colEnd)
    const allColumnIds = getColumnIds()

    selectedRanges.value = [
      {
        start: { rowIndex: allRowStart, colId: allColumnIds[allColStart] },
        end: { rowIndex: allRowEnd, colId: allColumnIds[allColEnd] },
      },
    ]

    currentRangeIndex.value = -1
    gridApi.value?.refreshCells({ force: true })
    updateSelectionRects()
    // updateFillHandlePosition will be called by the watcher
  }

  const onGridReady = (params: GridReadyEvent<GridRowData>) => {
    gridApi.value = params.api
    gridReady.value = true
    window.addEventListener('mouseup', handleMouseUp)
    window.addEventListener('mousemove', handleFillDragMove)

    // Listen for scroll inside AG Grid body to keep fill handle in sync
    nextTick(() => {
      scrollViewport = gridContainer.value?.querySelector('.ag-body-viewport') ?? null
      scrollViewport?.addEventListener('scroll', onBodyViewportScroll, { passive: true })

      if (gridContainer.value) {
        resizeObserver = new ResizeObserver(() => {
          updateAllRects()
        })
        resizeObserver.observe(gridContainer.value)
      }
    })
  }

  onUnmounted(() => {
    window.removeEventListener('mouseup', handleMouseUp)
    window.removeEventListener('mousemove', handleFillDragMove)
    scrollViewport?.removeEventListener('scroll', onBodyViewportScroll)
    resizeObserver?.disconnect()
  })

  const handleMouseUp = () => {
    if (fillDragging.value) {
      if (fillPreviewRange.value) {
        applyFill()
      }
      fillDragging.value = false
      fillSourceRange.value = null
      fillPreviewRange.value = null
      fillPreviewRect.value = null
      isSelecting.value = false
      currentRangeIndex.value = -1
    } else {
      const multiClickTarget = _lastMultiClickPoint
      _lastMultiClickPoint = null

      nextTick(() => {
        isSelecting.value = false
        _suppressFocusSync = false
        updateFillHandlePosition()

        // Ctrl+點擊後：明確把 focus 設置到最後點擊的格
        // 此時 _suppressFocusSync 已為 false，但 onCellFocused 內部會因多範圍而賭回 (return early)
        if (multiClickTarget && gridApi.value) {
          const col = gridApi.value.getAllDisplayedColumns().find(
            (c) => c.getColId() === multiClickTarget.colId
          )
          if (col) {
            gridApi.value.setFocusedCell(multiClickTarget.rowIndex, col)
          }
        }
      })

      const isSingleCell =
        selectedRanges.value.length === 1 &&
        selectedRanges.value[0].start.rowIndex === selectedRanges.value[0].end.rowIndex &&
        selectedRanges.value[0].start.colId === selectedRanges.value[0].end.colId

      if (!isSingleCell) {
        gridApi.value?.refreshCells({ force: true })
      }

      updateSelectionRects()
    }
  }

  // 記錄最後一次 Ctrl+點擊的格，用於 mouseup 後設定 focus
  let _lastMultiClickPoint: CellPoint | null = null

  const onCellMouseDown = (params: CellMouseDownEvent<GridRowData>) => {
    const event = params.event as MouseEvent
    const { node, column } = params

    if (event.button !== 0) return
    if (node.rowIndex === null) return

    _suppressFocusSync = true
    isSelecting.value = true
    const isMulti = event.ctrlKey || event.metaKey
    const newPoint = { rowIndex: node.rowIndex, colId: column.getId() }

    if (event.shiftKey && selectedRanges.value.length > 0) {
      // Shift+點擊：擴展最後一個範圍的終點
      currentRangeIndex.value = selectedRanges.value.length - 1
      selectedRanges.value[currentRangeIndex.value].end = newPoint
      _lastMultiClickPoint = null
    } else if (isMulti) {
      // Ctrl+點擊：新增一個範圍，結束後需要讓最後點擊的格有 focus
      selectedRanges.value.push({ start: newPoint, end: newPoint })
      currentRangeIndex.value = selectedRanges.value.length - 1
      _lastMultiClickPoint = newPoint
    } else {
      selectedRanges.value = [{ start: newPoint, end: newPoint }]
      currentRangeIndex.value = 0
      _lastMultiClickPoint = null
    }

    updateSelectionRects()

    if (isMulti || event.shiftKey) {
      params.api.refreshCells({ force: true })
    }
  }

  // RAF ID for throttling cell refresh during mouse-drag selection
  let _rafRefreshId: number | null = null

  const onCellMouseOver = (params: CellMouseOverEvent<GridRowData>) => {
    if (!isSelecting.value || currentRangeIndex.value === -1) return
    if (params.node.rowIndex === null) return

    const range = selectedRanges.value[currentRangeIndex.value]
    range.end = { rowIndex: params.node.rowIndex, colId: params.column.getId() }

    updateSelectionRects()

    // Throttle via requestAnimationFrame to avoid refreshing every single cell during drag
    if (_rafRefreshId !== null) cancelAnimationFrame(_rafRefreshId)
    _rafRefreshId = requestAnimationFrame(() => {
      params.api.refreshCells({ force: true })
      _rafRefreshId = null
    })
  }

  const onCellValueChanged = (params: CellValueChangedEvent<GridRowData>) => {
    // Only track manual edits (source: 'edit')
    if (params.source !== 'edit') return

    pushUndo([
      {
        rowIndex: params.node.rowIndex!,
        colId: params.column.getColId(),
        oldValue: params.oldValue,
        newValue: params.newValue,
      },
    ])
  }

  const getCellRawValue = (rowNode: IRowNode<GridRowData>, column: Column): unknown => {
    if (!gridApi.value || !rowNode) return undefined
    // AG Grid v31+ uses getCellValue with an object parameter
    return gridApi.value.getCellValue({
      rowNode: rowNode,
      colKey: column,
    })
  }

  const formatClipboardValue = (params: {
    rowNode: IRowNode<GridRowData>
    column: Column
    value: unknown
  }): string => {
    const { rowNode, column, value } = params
    if (value === null || value === undefined) {
      return ''
    }

    const colDef = column.getColDef() as GridColumnDef
    if (colDef.valueFormatter && typeof colDef.valueFormatter === 'function') {
      try {
        // Manually invoke the formatter with the standard AG Grid params object
        return colDef.valueFormatter({
          value,
          data: rowNode.data,
          node: rowNode,
          column,
          colDef,
          api: gridApi.value!,
          context: gridApi.value?.getGridOptions()?.context,
        })
      } catch (e) {
        console.warn('Value formatter failed during copy:', e)
        return String(value)
      }
    }

    if (value instanceof Date) {
      return value.toISOString()
    }

    return String(value)
  }

  const buildRangeClipboardRows = (range: CellRange, columnMap: Map<string, Column>): string[] => {
    const api = gridApi.value
    const normalizedRange = getNormalizedRange(range)

    if (!api || !normalizedRange) {
      return []
    }

    const rows: string[] = new Array(normalizedRange.rowEnd - normalizedRange.rowStart + 1)

    for (
      let rowIndex = normalizedRange.rowStart;
      rowIndex <= normalizedRange.rowEnd;
      rowIndex += 1
    ) {
      const rowNode = api.getDisplayedRowAtIndex(rowIndex)
      if (!rowNode) {
        rows[rowIndex - normalizedRange.rowStart] = ''
        continue
      }

      const rowValues = normalizedRange.columnIds.map((colId) => {
        const column = columnMap.get(colId)
        if (!column) return ''
        const value = getCellRawValue(rowNode, column)
        return formatClipboardValue({ rowNode, column, value })
      })

      rows[rowIndex - normalizedRange.rowStart] = rowValues.join('\t')
    }

    return rows
  }

  const buildClipboardText = (): string => {
    const api = gridApi.value
    const displayedColumns = getDisplayedColumns()

    if (!api || displayedColumns.length === 0) {
      return ''
    }

    const columnMap = new Map(displayedColumns.map((column) => [column.getColId(), column]))

    if (selectedRanges.value.length > 0) {
      // 建立所有被選取的 cell 座標（去重），然後按 row → col 排序產出 TSV
      const allColumnIds = getColumnIds()
      // key: "rowIndex:colId", value: formatted string
      const cellValues = new Map<string, string>()
      const rowSet = new Set<number>()

      for (const range of selectedRanges.value) {
        const normalized = getNormalizedRange(range)
        if (!normalized) continue
        for (let r = normalized.rowStart; r <= normalized.rowEnd; r++) {
          rowSet.add(r)
          const rowNode = api.getDisplayedRowAtIndex(r)
          if (!rowNode) continue
          for (const colId of normalized.columnIds) {
            const key = `${r}:${colId}`
            if (cellValues.has(key)) continue
            const column = columnMap.get(colId)
            if (!column) continue
            const value = getCellRawValue(rowNode, column)
            cellValues.set(key, formatClipboardValue({ rowNode, column, value }))
          }
        }
      }

      const sortedRows = Array.from(rowSet).sort((a, b) => a - b)

      // 找出所有被涵蓋的欄位（保持顯示順序）
      const coveredColIds = allColumnIds.filter((colId) =>
        sortedRows.some((r) => cellValues.has(`${r}:${colId}`))
      )

      return sortedRows
        .map((r) => coveredColIds.map((colId) => cellValues.get(`${r}:${colId}`) ?? '').join('\t'))
        .join('\n')
    }

    const selectedNodes = api.getSelectedNodes()

    if (selectedNodes.length === 0) {
      return ''
    }

    return selectedNodes
      .map((rowNode) => {
        return displayedColumns
          .map((column) => {
            const value = getCellRawValue(rowNode, column)
            return formatClipboardValue({ rowNode, column, value })
          })
          .join('\t')
      })
      .join('\n')
  }

  const parseClipboardText = (text: string): ClipboardMatrix => {
    if (!text) {
      return []
    }

    const lines = text.replace(/\r\n?/g, '\n').split('\n')

    while (lines.length > 0 && lines[lines.length - 1] === '') {
      lines.pop()
    }

    return lines.map((line) => line.split('\t'))
  }

  const isClipboardEventFromEditor = (target: EventTarget | null): boolean => {
    return (
      target instanceof HTMLElement &&
      Boolean(
        target.closest(
          'input, textarea, select, [contenteditable="true"], [contenteditable=""], .ag-cell-editor, .ag-select-editor, .ag-text-field-input-wrapper',
        ),
      )
    )
  }

  const buildColumnCallbackParams = <TValue,>(
    rowNode: IRowNode<GridRowData>,
    column: Column<TValue>,
  ) => {
    return {
      api: gridApi.value as GridApi<GridRowData>,
      context: undefined,
      node: rowNode,
      data: rowNode.data,
      column,
      colDef: column.getColDef() as ColDef<GridRowData, TValue>,
    }
  }

  const canPasteIntoCell = (rowNode: IRowNode<GridRowData>, column: Column): boolean => {
    if (!column.isCellEditable(rowNode)) {
      return false
    }

    const suppressPaste = column.getColDef().suppressPaste

    if (typeof suppressPaste === 'function') {
      return !suppressPaste(
        buildColumnCallbackParams(rowNode, column) as SuppressPasteCallbackParams<GridRowData>,
      )
    }

    return suppressPaste !== true
  }

  const parsePastedValue = (
    rowNode: IRowNode<GridRowData>,
    column: Column,
    rawValue: string,
  ): unknown => {
    const colDef = column.getColDef() as GridColumnDef
    const currentValue = getCellRawValue(rowNode, column)

    if (typeof colDef.valueParser === 'function' && colDef.useValueParserForImport !== false) {
      return colDef.valueParser({
        ...buildColumnCallbackParams(rowNode, column),
        oldValue: currentValue,
        newValue: rawValue,
      } as ValueParserParams<GridRowData>)
    }

    if (rawValue === '') {
      return null
    }

    const trimmedValue = rawValue.trim()
    const cellDataType = colDef.cellDataType

    if (cellDataType === 'number' || typeof currentValue === 'number') {
      const parsedNumber = Number(trimmedValue)
      return Number.isNaN(parsedNumber) ? currentValue : parsedNumber
    }

    if (cellDataType === 'boolean' || typeof currentValue === 'boolean') {
      if (/^(true|1|yes|y)$/i.test(trimmedValue)) {
        return true
      }

      if (/^(false|0|no|n)$/i.test(trimmedValue)) {
        return false
      }
    }

    return rawValue
  }

  const applyClipboardMatrix = (matrix: ClipboardMatrix): boolean => {
    const api = gridApi.value
    const displayedColumns = getDisplayedColumns()

    if (!api || matrix.length === 0 || displayedColumns.length === 0) {
      return false
    }

    const maxSourceColumnCount = Math.max(...matrix.map((row) => row.length), 0)

    if (maxSourceColumnCount === 0) {
      return false
    }

    const activeRange = selectedRanges.value[selectedRanges.value.length - 1]
    const normalizedRange = activeRange ? getNormalizedRange(activeRange) : null
    const columnIds = displayedColumns.map((column) => column.getColId())

    let shouldRepeatToFillSelection = false

    const anchor: CellPoint | null = normalizedRange
      ? {
          rowIndex: normalizedRange.rowStart,
          colId: normalizedRange.columnIds[0],
        }
      : getFocusedPoint()

    if (normalizedRange) {
      const targetRowCount = normalizedRange.rowEnd - normalizedRange.rowStart + 1
      const targetColumnCount = normalizedRange.colEnd - normalizedRange.colStart + 1

      shouldRepeatToFillSelection =
        selectedRanges.value.length === 1 &&
        targetRowCount >= matrix.length &&
        targetColumnCount >= maxSourceColumnCount &&
        targetRowCount % matrix.length === 0 &&
        targetColumnCount % maxSourceColumnCount === 0 &&
        (targetRowCount !== matrix.length || targetColumnCount !== maxSourceColumnCount)
    }

    if (!anchor) {
      return false
    }

    const anchorColumnIndex = columnIds.indexOf(anchor.colId)

    if (anchorColumnIndex === -1) {
      return false
    }

    api.stopEditing()

    let lastVisited: CellPoint | null = null
    const undoEntries: UndoEntry = []

    if (shouldRepeatToFillSelection && normalizedRange) {
      for (
        let rowIndex = normalizedRange.rowStart;
        rowIndex <= normalizedRange.rowEnd;
        rowIndex += 1
      ) {
        const rowNode = api.getDisplayedRowAtIndex(rowIndex)

        if (!rowNode) {
          continue
        }

        const sourceRow = matrix[(rowIndex - normalizedRange.rowStart) % matrix.length]

        for (
          let columnIndex = normalizedRange.colStart;
          columnIndex <= normalizedRange.colEnd;
          columnIndex += 1
        ) {
          const targetColumn = displayedColumns[columnIndex]

          if (!targetColumn || !canPasteIntoCell(rowNode, targetColumn)) {
            continue
          }

          const rawValue =
            sourceRow[(columnIndex - normalizedRange.colStart) % sourceRow.length] ?? ''
          const newValue = parsePastedValue(rowNode, targetColumn, rawValue)
          undoEntries.push({
            rowIndex,
            colId: targetColumn.getColId(),
            oldValue: getCellRawValue(rowNode, targetColumn),
            newValue,
          })
          rowNode.setDataValue(targetColumn, newValue, 'paste')
          lastVisited = { rowIndex, colId: targetColumn.getColId() }
        }
      }
    } else {
      for (let rowOffset = 0; rowOffset < matrix.length; rowOffset += 1) {
        const rowNode = api.getDisplayedRowAtIndex(anchor.rowIndex + rowOffset)

        if (!rowNode) {
          continue
        }

        const sourceRow = matrix[rowOffset]

        for (let columnOffset = 0; columnOffset < sourceRow.length; columnOffset += 1) {
          const targetColumn = displayedColumns[anchorColumnIndex + columnOffset]

          if (!targetColumn || !canPasteIntoCell(rowNode, targetColumn)) {
            continue
          }

          const targetRowIndex = anchor.rowIndex + rowOffset
          const rawValue = sourceRow[columnOffset]
          const newValue = parsePastedValue(rowNode, targetColumn, rawValue)
          undoEntries.push({
            rowIndex: targetRowIndex,
            colId: targetColumn.getColId(),
            oldValue: getCellRawValue(rowNode, targetColumn),
            newValue,
          })
          rowNode.setDataValue(targetColumn, newValue, 'paste')
          lastVisited = { rowIndex: targetRowIndex, colId: targetColumn.getColId() }
        }
      }
    }

    if (!lastVisited) {
      return false
    }

    pushUndo(undoEntries)

    if (!shouldRepeatToFillSelection) {
      selectedRanges.value = [{ start: anchor, end: lastVisited }]
      currentRangeIndex.value = -1
    }

    updateSelectionRects()
    api.refreshCells({ force: true })
    focusCell(anchor)

    return true
  }

  /**
   * 使用 capture 階段攔截 Ctrl+C / Ctrl+V。
   * 這比監聽 copy/paste DOM 事件更可靠，因為 AG Grid 有機會在
   * bubble 階段消化 clipboard 事件，導致事件到不了我們的 wrapper div。
   * Capture 階段在 AG Grid 收到事件之前就能執行，確保一定會被觸發。
   *
   * 注意：stopPropagation 和 preventDefault 必須在 await 之前同步呼叫。
   * async function 在遇到第一個 await 前仍屬同步，因此時序是正確的。
   */
  const onKeyDownCapture = async (event: KeyboardEvent) => {
    // ─── Shift+Arrow: 範圍選取擴展 ──────────────────────────────────────────
    // 必須在 capture 階段處理，因為 AG Grid 會在 bubble 階段內部處理箭頭鍵導航，
    // 導致 focus 移動後觸發 onCellFocused 重置 selectedRanges。
    // 在 capture 階段攔截就能完全阻止 AG Grid 看到此事件。
    if (
      event.shiftKey &&
      !event.ctrlKey && !event.metaKey && !event.altKey &&
      ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)
    ) {
      const api = gridApi.value
      if (!api) return
      if (isClipboardEventFromEditor(event.target)) return
      if (api.getEditingCells().length > 0) return

      const focusedCell = api.getFocusedCell()
      if (!focusedCell || focusedCell.rowIndex === null) return

      event.preventDefault()
      event.stopPropagation()

      const focusRowIndex = focusedCell.rowIndex
      const focusColId = focusedCell.column.getColId()

      // 確保有範圍可擴展
      if (selectedRanges.value.length === 0) {
        const anchor = { rowIndex: focusRowIndex, colId: focusColId }
        selectedRanges.value = [{ start: anchor, end: anchor }]
        currentRangeIndex.value = 0
      } else if (currentRangeIndex.value === -1) {
        currentRangeIndex.value = selectedRanges.value.length - 1
      }

      const range = selectedRanges.value[currentRangeIndex.value]
      if (!range) return

      // 若範圍是單格且與 focused cell 不匹配，以 focused cell 重建 anchor
      if (
        range.start.rowIndex === range.end.rowIndex &&
        range.start.colId === range.end.colId &&
        (range.start.rowIndex !== focusRowIndex || range.start.colId !== focusColId)
      ) {
        const anchor = { rowIndex: focusRowIndex, colId: focusColId }
        selectedRanges.value[currentRangeIndex.value] = { start: anchor, end: anchor }
      }

      const liveRange = selectedRanges.value[currentRangeIndex.value]

      let nextRowIndex = liveRange.end.rowIndex
      const columnIds = api.getAllDisplayedColumns().map((col) => col.getColId())
      let colIdx = columnIds.indexOf(liveRange.end.colId)

      if (event.key === 'ArrowUp') nextRowIndex = Math.max(0, nextRowIndex - 1)
      if (event.key === 'ArrowDown') nextRowIndex = Math.min(api.getDisplayedRowCount() - 1, nextRowIndex + 1)
      if (event.key === 'ArrowLeft') colIdx = Math.max(0, colIdx - 1)
      if (event.key === 'ArrowRight') colIdx = Math.min(columnIds.length - 1, colIdx + 1)

      liveRange.end = { rowIndex: nextRowIndex, colId: columnIds[colIdx] }
      updateSelectionRects()
      api.refreshCells({ force: true })

      api.ensureIndexVisible(liveRange.end.rowIndex)
      api.ensureColumnVisible(liveRange.end.colId)
      return
    }

    // Escape: 清除複製狀態（螞蟻行軍）。若在編輯中則不干涉，讓 AG Grid 自己處理取消編輯
    if (event.key === 'Escape' && !isClipboardEventFromEditor(event.target)) {
      if (copyRanges.value.length > 0) {
        clearCopyState()
      }
      return
    }

    // Enter: 不在 editor 內 → 啟動編輯；在 editor 內 → 讓 editor 自己處理（不干涉）
    if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
      const api = gridApi.value
      if (!api) return

      // If we're already editing, let the grid handle it (bubble phase)
      if (api.getEditingCells().length > 0) {
        return
      }

      const focusedCell = api.getFocusedCell()
      if (focusedCell && focusedCell.rowIndex !== null && !focusedCell.rowPinned) {
        event.preventDefault()
        event.stopPropagation()
        api.startEditingCell({ rowIndex: focusedCell.rowIndex, colKey: focusedCell.column })
      }
      return
    }

    // Delete / Backspace:
    // Excel behavior: Backspace on a cell starts editing with empty value (Esc restores).
    // Delete usually just clears (Undo restores). To satisfy "Esc restores for Delete",
    // we make single-cell Delete also start editing with an empty value.
    if (
      (event.key === 'Delete' || event.key === 'Backspace') &&
      !event.shiftKey &&
      !event.ctrlKey &&
      !event.metaKey
    ) {
      const api = gridApi.value
      if (!api || isClipboardEventFromEditor(event.target)) return

      const focusedCell = api.getFocusedCell()
      const isRange =
        selectedRanges.value.length > 1 ||
        (selectedRanges.value.length === 1 &&
          (selectedRanges.value[0].start.rowIndex !== selectedRanges.value[0].end.rowIndex ||
            selectedRanges.value[0].start.colId !== selectedRanges.value[0].end.colId))

      // For single-cell selection, start editing with an empty string so Esc can restore the value.
      if (!isRange && focusedCell && focusedCell.rowIndex !== null && !focusedCell.rowPinned) {
        event.preventDefault()
        event.stopPropagation()
        api.startEditingCell({
          rowIndex: focusedCell.rowIndex,
          colKey: focusedCell.column,
          charPress: '',
        })
        return
      }

      // For multi-cell/range selection, perform a bulk delete (restorable via Ctrl+Z).
      event.preventDefault()
      event.stopPropagation()

      api.stopEditing()
      const undoEntries: UndoEntry = []
      const displayedColumns = getDisplayedColumns()
      const colMap = new Map(displayedColumns.map((c) => [c.getColId(), c]))

      selectedRanges.value.forEach((range) => {
        const normalized = getNormalizedRange(range)
        if (!normalized) return

        for (let r = normalized.rowStart; r <= normalized.rowEnd; r++) {
          const rowNode = api.getDisplayedRowAtIndex(r)
          if (!rowNode) continue

          normalized.columnIds.forEach((colId) => {
            const column = colMap.get(colId)
            if (!column || !canPasteIntoCell(rowNode, column)) return

            undoEntries.push({
              rowIndex: r,
              colId,
              oldValue: getCellRawValue(rowNode, column),
              newValue: null,
            })
            rowNode.setDataValue(column, null, 'delete')
          })
        }
      })

      if (undoEntries.length > 0) {
        pushUndo(undoEntries)
      }
      return
    }

    // Ctrl/Cmd 一定必須存在，且不能是 Alt 組合
    // 注意：此處保留 shiftKey 允許通達，地 Ctrl+Shift+Z 能正常觸發 Redo
    if (!(event.ctrlKey || event.metaKey) || event.altKey) {
      return
    }

    if (isClipboardEventFromEditor(event.target)) {
      return
    }

    const key = event.key.toLowerCase()

    if (key === 'z') {
      const api = gridApi.value
      if (api && api.getEditingCells().length > 0) {
        api.stopEditing(false)
      }

      if (event.shiftKey) {
        // Redo (Ctrl+Shift+Z or Cmd+Shift+Z)
        if (redoStack.length > 0) {
          event.preventDefault()
          event.stopPropagation()
          applyRedo()
        }
      } else {
        // Undo (Ctrl+Z)
        if (undoStack.length > 0) {
          event.preventDefault()
          event.stopPropagation()
          applyUndo()
        }
      }
      return
    }

    if (key === 'y' && !event.shiftKey) {
      // Redo (Ctrl+Y)
      if (redoStack.length > 0) {
        event.preventDefault()
        event.stopPropagation()
        applyRedo()
      }
      return
    }

    if (key === 'c') {
      const text = buildClipboardText()

      if (!text) {
        return
      }

      event.preventDefault()
      event.stopPropagation()

      // Save copy ranges for visual feedback (like Excel's marching ants)
      copyRanges.value = selectedRanges.value.map((r) => ({
        start: { ...r.start },
        end: { ...r.end },
      }))
      updateCopyRects()

      try {
        await navigator.clipboard.writeText(text)
      } catch {
        // Clipboard write API not available
      }
      return
    }

    if (key === 'v') {
      event.preventDefault()
      event.stopPropagation()
      clearCopyState()

      try {
        const text = await navigator.clipboard.readText()
        const matrix = parseClipboardText(text)

        if (matrix.length > 0) {
          applyClipboardMatrix(matrix)
        }
      } catch {
        // Clipboard read API not available or permission denied
      }
      return
    }
  }

  const defaultColDef: GridColumnDef = {
    flex: 1,
    minWidth: 100,
    resizable: true,
    sortable: true,
    filter: true,
    editable: true,
    suppressMovable: false,
    cellClassRules: {
      'custom-range-selected': (params: { node: IRowNode<GridRowData>; column: Column }) => {
        if (params.node.rowIndex === null) {
          return false
        }

        return isCellSelected(params.node.rowIndex, params.column.getColId())
      },
    },
  }

  const clearSelections = () => {
    selectedRanges.value = []
    currentRangeIndex.value = -1
    updateSelectionRects()
    gridApi.value?.refreshCells({ force: true })
    clearCopyState()
  }

  const copySelected = async () => {
    const text = buildClipboardText()

    if (!text || !navigator.clipboard?.writeText) {
      return
    }

    await navigator.clipboard.writeText(text)
  }

  const onCellKeyDown = (params: CellKeyDownEvent<GridRowData>) => {
    const event = params.event as KeyboardEvent
    const rowIndex = params.node.rowIndex
    const { column, api } = params

    if (event.key === 'Escape') {
      clearSelections()
      return
    }

    // Ctrl + A: Select All
    if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
      event.preventDefault()
      const rowCount = api.getDisplayedRowCount()
      const allColumns = api.getAllDisplayedColumns()
      if (rowCount > 0 && allColumns.length > 0) {
        selectedRanges.value = [{
          start: { rowIndex: 0, colId: allColumns[0].getColId() },
          end: { rowIndex: rowCount - 1, colId: allColumns[allColumns.length - 1].getColId() }
        }]
        currentRangeIndex.value = 0
        updateSelectionRects()
        api.refreshCells({ force: true })
        // 更新 fillHandle 位置（Ctrl+A 後需顯示在右下角最後一格）
        updateAllRects()
      }
      return
    }

    // Shift+Arrow 已移至 onKeyDownCapture（capture 階段）處理，此處不再處理
  }

  // ─── Cell Focused: sync selection when AG Grid moves focus (Arrow keys etc.) ──

  let _suppressFocusSync = false

  const onCellFocused = (event: CellFocusedEvent<GridRowData>) => {
    if (_suppressFocusSync) return
    if (isSelecting.value) return
    if (event.rowIndex === null || event.rowPinned) return

    const col = event.column as Column | null
    if (!col || typeof col.getColId !== 'function') return
    const colId = col.getColId()

    const newPoint: CellPoint = { rowIndex: event.rowIndex, colId }

    // 若目前是多範圍選取狀態（Ctrl+點擊產生），僅更新 focus 記錄不重置整組 selectedRanges
    // （有多個範圍時 onCellFocused 不應該清除其它範圍）
    if (selectedRanges.value.length > 1) {
      // 每次 focus 移動到新格，不重置多選狀態，只記錄 currentRangeIndex
      return
    }

    // 單範圍或無範圍時：正常同步
    selectedRanges.value = [{ start: newPoint, end: newPoint }]
    currentRangeIndex.value = 0
    updateSelectionRects()

    const isSingleCell =
      selectedRanges.value.length === 1 &&
      selectedRanges.value[0].start.rowIndex === selectedRanges.value[0].end.rowIndex &&
      selectedRanges.value[0].start.colId === selectedRanges.value[0].end.colId

    if (!isSingleCell) {
      event.api.refreshCells({ force: true })
    }
  }

  defineExpose({
    gridApi,
    copySelected,
  })
</script>

<template>
  <!--
    The key to dark mode: set data-ag-theme-mode on a parent element.
    themeQuartz uses colorSchemeVariable by default, which reads this attribute.
  -->
  <div
    ref="gridContainer"
    :data-ag-theme-mode="themeMode"
    class="w-full overflow-hidden border rounded-xl shadow-sm transition-colors duration-300"
    :class="isDark ? 'border-slate-700/50' : 'border-slate-200'"
    :style="{ height: typeof height === 'number' ? height + 'px' : height, position: 'relative' }"
    @keydown.capture="onKeyDownCapture"
  >
    <AgGridVue
      v-bind="gridOptions"
      class="w-full h-full"
      :theme="gridTheme"
      :row-data="rowData"
      :column-defs="columnDefs"
      :default-col-def="defaultColDef"
      :animate-rows="true"
      :row-selection="'multiple'"
      :suppress-row-click-selection="true"
      :enable-cell-text-selection="false"
      :ensure-dom-order="true"
      :undo-redo-cell-editing="false"
      @grid-ready="onGridReady"
      @body-scroll="onBodyScroll"
      @column-resized="updateAllRects"
      @column-moved="updateAllRects"
      @column-visible="updateAllRects"
      @displayed-columns-changed="updateAllRects"
      @cell-key-down="onCellKeyDown"
      @cell-mouse-down="onCellMouseDown"
      @cell-mouse-over="onCellMouseOver"
      @cell-focused="onCellFocused"
      @cell-value-changed="onCellValueChanged"
    />

    <!-- 
      Overlays are teleported into the AG Grid root so they respect internal layering.
      We use a clip-path to ensure the selection border is hidden under the pinned columns
      when scrolling, satisfying the "covered by frozen columns" requirement.
    -->
    <Teleport v-if="gridReady && gridContainer" :to="gridContainer.querySelector('.ag-root')">
      <div
        class="ag-custom-overlays-container"
        :style="{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 10,
          clipPath: `inset(0 ${getPinnedRightWidth()}px 0 ${getPinnedLeftWidth()}px)`,
        }"
      >
        <!-- Fill Handle: small square at bottom-right corner of selection -->
        <div
          v-if="fillHandlePos && selectedRanges.length > 0 && !fillDragging && !isSelecting"
          class="fill-handle"
          :style="{ left: fillHandlePos.left + 'px', top: fillHandlePos.top + 'px' }"
          @mousedown="onFillHandleMouseDown"
        />

        <!-- Fill Preview: dashed overlay shown while dragging fill handle -->
        <div
          v-if="fillDragging && fillPreviewRect"
          class="fill-preview"
          :style="{
            left: fillPreviewRect.left + 'px',
            top: fillPreviewRect.top + 'px',
            width: fillPreviewRect.width + 'px',
            height: fillPreviewRect.height + 'px',
          }"
        />

        <!-- Selection Range Overlays: clean outer border around each selected range -->
        <div
          v-for="(rect, i) in selectionRects"
          :key="'sel-' + i"
          class="selection-range-overlay"
          :style="{
            left: rect.left + 'px',
            top: rect.top + 'px',
            width: rect.width + 'px',
            height: rect.height + 'px',
          }"
        />

        <!-- Copy Range Overlays: animated dashed border indicating copied area (like Excel marching ants) -->
        <div
          v-for="(rect, i) in copyRects"
          :key="'copy-' + i"
          class="copy-range-overlay"
          :style="{
            left: rect.left + 'px',
            top: rect.top + 'px',
            width: rect.width + 'px',
            height: rect.height + 'px',
          }"
        />
      </div>
    </Teleport>
  </div>
</template>

<style>
  /* --- Notion-like Global Adjustments --- */
  .ag-theme-quartz,
  .ag-theme-quartz-dark {
    --ag-border-radius: 6px;
    --ag-grid-size: 6px;
    --ag-list-item-height: 32px;
  }

  /* Custom Selection Border (Primary Color) */
  .ag-cell-focus:not(.ag-cell-editing) {
    border: 2px solid hsl(var(--primary)) !important;
    outline: none !important;
  }

  /* Hide default editor border to avoid double border */
  .ag-cell-editing {
    border: 2px solid hsl(var(--primary)) !important;
    padding: 0 !important;
  }

  /* Fill Handle square (real DOM element, positioned at bottom-right of selection) */
  .fill-handle {
    position: absolute;
    width: 8px;
    height: 8px;
    background-color: hsl(var(--primary));
    border: 1.5px solid white;
    border-radius: 1px;
    z-index: 200;
    cursor: crosshair;
    transform: translate(-50%, -50%);
    pointer-events: all;
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15);
  }

  /* Fill Preview overlay - dashed border shown while dragging fill handle */
  .fill-preview {
    position: absolute;
    pointer-events: none;
    border: 2px dashed hsl(var(--primary));
    background-color: color-mix(in srgb, hsl(var(--primary)) 5%, transparent);
    z-index: 150;
  }

  /* Remove horizontal lines between header cells for a cleaner look */
  .ag-header-cell::after {
    display: none !important;
  }

  /* Header Text Style */
  .ag-header-cell-label {
    font-weight: 500 !important;
    text-transform: none;
    letter-spacing: normal;
  }

  /* Selected row highlight */
  .ag-row-selected {
    background-color: color-mix(
      in srgb,
      var(--ag-accent-color, #2563eb) 8%,
      var(--ag-background-color, #fff)
    ) !important;
  }

  /* Custom Range Selection Style: background tint only, border handled by overlay */
  .ag-theme-quartz .ag-cell.custom-range-selected,
  .ag-theme-quartz-dark .ag-cell.custom-range-selected {
    background-color: color-mix(in srgb, hsl(var(--primary)) 12%, transparent) !important;
  }

  /* Selection range overlay: single outer border around the entire selection */
  .selection-range-overlay {
    position: absolute;
    pointer-events: none;
    border: 2px solid color-mix(in srgb, hsl(var(--primary)) 80%, transparent);
    z-index: 10;
  }

  /* Copy range overlay: animated dashed border indicating copied cells */
  .copy-range-overlay {
    position: absolute;
    pointer-events: none;
    border: 2px dashed hsl(var(--primary));
    z-index: 20;
    animation: copyRangePulse 0.75s ease-in-out infinite alternate;
  }

  @keyframes copyRangePulse {
    from {
      opacity: 1;
    }
    to {
      opacity: 0.4;
    }
  }

  /* Focus cell should still have its primary border */
  .ag-theme-quartz .ag-cell-focus.custom-range-selected,
  .ag-theme-quartz-dark .ag-cell-focus.custom-range-selected {
    background-color: color-mix(in srgb, hsl(var(--primary)) 20%, transparent) !important;
  }

  /* Drag indicator - help user know they are selecting */
  .ag-body-viewport {
    cursor: cell; /* Changes cursor to a crosshair/cell cursor */
  }
</style>
