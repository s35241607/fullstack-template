export type PoReceiptGapStatus = 'late' | 'risk' | 'onTrack' | 'ahead'

export interface PoReceiptMatrixRow extends Record<string, unknown> {
  id: string
  rowIndexInLine: number
  lineBandIndex: number
  isLineStart: boolean
  poNumber: string
  poLineId: string
  poLineLabel: string
  poLineNumber: string
  supplierName: string
  buyerName: string
  plantCode: string
  itemCode: string
  itemName: string
  lineOrderedQuantity: number
  lineReceiptQuantity: number
  lineOpenQuantity: number
  lineReceiptRate: number
  scheduleCount: number
  targetCount: number
  scheduleSpanKey: string | null
  scheduleNo: string | null
  commitDate: string | null
  scheduleQuantity: number | null
  scheduleOpenQuantity: number | null
  scheduleReceiptQuantity: number | null
  scheduleBalanceQuantity: number | null
  targetSpanKey: string | null
  targetDate: string | null
  targetQuantity: number | null
  targetRangeLabel: string | null
  mappedQuantity: number | null
  mappedRangeLabel: string | null
  targetGapDays: number | null
  targetGapStatus: PoReceiptGapStatus | null
}

export interface PoReceiptMatrixLookups {
  suppliers: string[]
  buyers: string[]
  plants: string[]
}

export interface PoReceiptMatrixSummary {
  poCount: number
  poLineCount: number
  displayRowCount: number
  scheduleCount: number
  targetCount: number
  openQuantity: number
  receiptQuantity: number
  worstGapDays: number
}

export interface PoReceiptMatrixDataset {
  rows: PoReceiptMatrixRow[]
  lookups: PoReceiptMatrixLookups
  summary: PoReceiptMatrixSummary
  loadedAt: string
}

interface DeliverySplit {
  scheduleIndex: number
  scheduleSpanKey: string
  scheduleNo: string
  commitDate: string
  scheduleQuantity: number
  scheduleOpenQuantity: number
  scheduleReceiptQuantity: number
  scheduleBalanceQuantity: number
  rangeStart: number
  rangeEnd: number
}

interface TargetSplit {
  targetIndex: number
  targetSpanKey: string
  targetDate: string
  targetQuantity: number
  targetRangeLabel: string
  targetGapDays: number
  targetGapStatus: PoReceiptGapStatus
  rangeStart: number
  rangeEnd: number
}

const suppliers = [
  '台積電先進封裝',
  '鴻海 (Foxconn)',
  '日月光 (ASE)',
  '德州儀器 (TI)',
  '村田 (Murata)',
  '億光 (Everlight)',
  '聯電整合材料',
  '京元電子',
]

const buyers = ['Kelly Lin', 'Ryan Wu', 'Ariel Chen', 'Mina Hsu', 'Jason Lai', 'Ivy Cheng']
const plants = ['Hsinchu-A', 'Taichung-B', 'Tainan-C', 'Kunshan-D']
const items = [
  { itemCode: 'PMIC-8921', itemName: 'PMIC 電源管理晶片' },
  { itemCode: 'MLCC-0402', itemName: 'MLCC 0402 被動元件' },
  { itemCode: 'USB-C-240W', itemName: 'USB-C 高速連接器' },
  { itemCode: 'OSC-24M', itemName: '24MHz 石英振盪器' },
  { itemCode: 'HSNK-AL', itemName: '散熱模組 (鋁心)' },
  { itemCode: 'LED-GRN', itemName: '綠光 LED 指示燈' },
  { itemCode: 'MCU-32', itemName: '32-bit 微控制器' },
  { itemCode: 'IND-10UH', itemName: '高頻電感 10uH' },
]

function wait(ms = 180) {
  return new Promise((resolve) => globalThis.setTimeout(resolve, ms))
}

function cloneValue<T>(value: T): T {
  if (typeof structuredClone === 'function') {
    return structuredClone(value)
  }

  return JSON.parse(JSON.stringify(value)) as T
}

function toIsoDate(date: Date) {
  return date.toISOString().slice(0, 10)
}

function addDays(date: string, days: number) {
  const next = new Date(`${date}T00:00:00.000Z`)
  next.setUTCDate(next.getUTCDate() + days)
  return toIsoDate(next)
}

function getGapStatus(gapDays: number): PoReceiptGapStatus {
  if (gapDays >= 7) return 'late'
  if (gapDays >= 1) return 'risk'
  if (gapDays < 0) return 'ahead'
  return 'onTrack'
}

function splitQuantity(totalQuantity: number, splitCount: number, seed: number) {
  const weights = Array.from({ length: splitCount }, (_, index) => 11 + ((seed + index * 7) % 13))
  const weightTotal = weights.reduce((sum, weight) => sum + weight, 0)
  let assigned = 0

  return weights.map((weight, index) => {
    if (index === splitCount - 1) {
      return totalQuantity - assigned
    }

    const quantity = Math.max(Math.round((totalQuantity * weight) / weightTotal), 1)
    assigned += quantity
    return quantity
  })
}

function allocateReceipts(scheduleQuantities: number[], receivedTotal: number) {
  let remaining = receivedTotal

  return scheduleQuantities.map((quantity) => {
    const receiptQuantity = Math.min(quantity, remaining)
    remaining -= receiptQuantity
    return receiptQuantity
  })
}

function uniqueSorted(values: string[]) {
  return Array.from(new Set(values)).sort((left, right) => left.localeCompare(right, 'zh-Hant'))
}

function formatRangeValue(quantity: number) {
  return quantity.toLocaleString('en-US')
}

function buildRangeLabel(rangeStart: number, rangeEnd: number) {
  return `${formatRangeValue(rangeStart)} - ${formatRangeValue(rangeEnd)}`
}

export function summarizePoReceiptMatrixRows(rows: PoReceiptMatrixRow[]): PoReceiptMatrixSummary {
  const poSet = new Set<string>()
  const poLineSet = new Set<string>()
  const scheduleSet = new Set<string>()
  const targetSet = new Set<string>()
  let scheduleCount = 0
  let targetCount = 0
  let openQuantity = 0
  let receiptQuantity = 0
  let worstGapDays = Number.NEGATIVE_INFINITY

  for (const row of rows) {
    poSet.add(row.poNumber)
    poLineSet.add(row.poLineId)

    if (row.scheduleSpanKey && !scheduleSet.has(row.scheduleSpanKey)) {
      scheduleSet.add(row.scheduleSpanKey)
      scheduleCount += 1
      openQuantity += row.scheduleOpenQuantity ?? 0
      receiptQuantity += row.scheduleReceiptQuantity ?? 0
    }

    if (row.targetSpanKey && !targetSet.has(row.targetSpanKey)) {
      targetSet.add(row.targetSpanKey)
      targetCount += 1
      worstGapDays = Math.max(worstGapDays, row.targetGapDays ?? Number.NEGATIVE_INFINITY)
    }
  }

  return {
    poCount: poSet.size,
    poLineCount: poLineSet.size,
    displayRowCount: rows.length,
    scheduleCount,
    targetCount,
    openQuantity,
    receiptQuantity,
    worstGapDays: Number.isFinite(worstGapDays) ? worstGapDays : 0,
  }
}

function buildRows() {
  const rows: PoReceiptMatrixRow[] = []
  let lineBandIndex = 0

  for (let poIndex = 0; poIndex < 160; poIndex++) {
    const poNumber = `PO-2026-${String(1001 + poIndex).padStart(4, '0')}`
    const buyerName = buyers[poIndex % buyers.length]
    const supplierName = suppliers[(poIndex * 3) % suppliers.length]
    const orderDate = toIsoDate(new Date(Date.UTC(2026, 0, 6 + (poIndex % 70))))
    const lineCount = 3 + ((poIndex * 5) % 4)

    for (let lineIndex = 0; lineIndex < lineCount; lineIndex++) {
      const poLineNumber = String(lineIndex + 1).padStart(2, '0')
      const poLineId = `${poNumber}-L${poLineNumber}`
      const item = items[(poIndex + lineIndex * 2) % items.length]
      const plantCode = plants[(poIndex + lineIndex) % plants.length]
      const orderedQuantity = 1200 + ((poIndex * 173 + lineIndex * 211) % 5800)
      const scheduleCount = 2 + ((poIndex + lineIndex) % 4)
      const scheduleQuantities = splitQuantity(
        orderedQuantity,
        scheduleCount,
        poIndex * 19 + lineIndex * 11,
      )
      const receiptRatio = (18 + ((poIndex * 11 + lineIndex * 7) % 67)) / 100
      const lineReceiptQuantity = Math.min(
        Math.round(orderedQuantity * receiptRatio),
        orderedQuantity,
      )
      const receiptAllocations = allocateReceipts(scheduleQuantities, lineReceiptQuantity)
      const scheduleOpenQuantities = scheduleQuantities.map(
        (scheduleQuantity, scheduleIndex) => scheduleQuantity - receiptAllocations[scheduleIndex],
      )
      const scheduleBalanceQuantities = scheduleOpenQuantities.map((_, scheduleIndex) =>
        scheduleOpenQuantities
          .slice(scheduleIndex)
          .reduce((sum, scheduleOpenQuantity) => sum + scheduleOpenQuantity, 0),
      )
      const lineOpenQuantity = orderedQuantity - lineReceiptQuantity
      const lineReceiptRate = orderedQuantity > 0 ? lineReceiptQuantity / orderedQuantity : 0
      let scheduleRangeEnd = 0
      const schedules: DeliverySplit[] = scheduleQuantities.map(
        (scheduleQuantity, scheduleIndex) => ({
          scheduleIndex,
          scheduleSpanKey: `${poLineId}-S${String(scheduleIndex + 1).padStart(2, '0')}`,
          scheduleNo: `S${String(scheduleIndex + 1).padStart(2, '0')}`,
          commitDate: addDays(
            orderDate,
            20 + scheduleIndex * 11 + ((poIndex * 5 + lineIndex * 3 + scheduleIndex) % 7),
          ),
          scheduleQuantity,
          scheduleOpenQuantity: scheduleOpenQuantities[scheduleIndex],
          scheduleReceiptQuantity: receiptAllocations[scheduleIndex],
          scheduleBalanceQuantity: scheduleBalanceQuantities[scheduleIndex],
          rangeStart: scheduleRangeEnd + 1,
          rangeEnd: (scheduleRangeEnd += scheduleQuantity),
        }),
      )

      const targetCount = 2 + ((poIndex * 2 + lineIndex * 3) % 4)
      const targetQuantities = splitQuantity(
        orderedQuantity,
        targetCount,
        poIndex * 31 + lineIndex * 17 + 9,
      )
      let allocatedTargetQuantity = 0
      const targets: TargetSplit[] = targetQuantities.map((targetQuantity, targetIndex) => {
        const mappedScheduleIndex = Math.min(
          Math.floor((targetIndex * scheduleCount) / targetCount),
          scheduleCount - 1,
        )
        const mappedSchedule = schedules[mappedScheduleIndex]
        const gapDays = -4 + ((poIndex * 7 + lineIndex * 5 + targetIndex * 3) % 17)
        const rangeStart = allocatedTargetQuantity + 1

        allocatedTargetQuantity += targetQuantity

        return {
          targetIndex,
          targetSpanKey: `${poLineId}-T${String(targetIndex + 1).padStart(2, '0')}`,
          targetDate: addDays(mappedSchedule.commitDate, -gapDays),
          targetQuantity,
          targetRangeLabel: buildRangeLabel(rangeStart, allocatedTargetQuantity),
          targetGapDays: gapDays,
          targetGapStatus: getGapStatus(gapDays),
          rangeStart,
          rangeEnd: allocatedTargetQuantity,
        }
      })

      const lineRows: PoReceiptMatrixRow[] = []
      let schedulePointer = 0
      let targetPointer = 0

      while (schedulePointer < schedules.length && targetPointer < targets.length) {
        const schedule = schedules[schedulePointer]
        const target = targets[targetPointer]
        const mappedRangeStart = Math.max(schedule.rangeStart, target.rangeStart)
        const mappedRangeEnd = Math.min(schedule.rangeEnd, target.rangeEnd)

        if (mappedRangeStart <= mappedRangeEnd) {
          lineRows.push({
            id: `${poLineId}-R${String(lineRows.length + 1).padStart(2, '0')}`,
            rowIndexInLine: lineRows.length,
            lineBandIndex,
            isLineStart: lineRows.length === 0,
            poNumber,
            poLineId,
            poLineLabel: `${poNumber} / ${poLineNumber}`,
            poLineNumber,
            supplierName,
            buyerName,
            plantCode,
            itemCode: item.itemCode,
            itemName: item.itemName,
            lineOrderedQuantity: orderedQuantity,
            lineReceiptQuantity,
            lineOpenQuantity,
            lineReceiptRate,
            scheduleCount,
            targetCount,
            scheduleSpanKey: schedule.scheduleSpanKey,
            scheduleNo: schedule.scheduleNo,
            commitDate: schedule.commitDate,
            scheduleQuantity: schedule.scheduleQuantity,
            scheduleOpenQuantity: schedule.scheduleOpenQuantity,
            scheduleReceiptQuantity: schedule.scheduleReceiptQuantity,
            scheduleBalanceQuantity: schedule.scheduleBalanceQuantity,
            targetSpanKey: target.targetSpanKey,
            targetDate: target.targetDate,
            targetQuantity: target.targetQuantity,
            targetRangeLabel: target.targetRangeLabel,
            mappedQuantity: mappedRangeEnd - mappedRangeStart + 1,
            mappedRangeLabel: buildRangeLabel(mappedRangeStart, mappedRangeEnd),
            targetGapDays: target.targetGapDays,
            targetGapStatus: target.targetGapStatus,
          })
        }

        if (schedule.rangeEnd <= mappedRangeEnd) {
          schedulePointer += 1
        }

        if (target.rangeEnd <= mappedRangeEnd) {
          targetPointer += 1
        }
      }

      rows.push(...lineRows)
      lineBandIndex += 1
    }
  }

  return rows
}

const matrixRows = buildRows()
const matrixLookups: PoReceiptMatrixLookups = {
  suppliers: uniqueSorted(matrixRows.map((row) => row.supplierName)),
  buyers: uniqueSorted(matrixRows.map((row) => row.buyerName)),
  plants: uniqueSorted(matrixRows.map((row) => row.plantCode)),
}
const matrixSummary = summarizePoReceiptMatrixRows(matrixRows)

export const poReceiptPivotMockApi = {
  getDataset: async (): Promise<PoReceiptMatrixDataset> => {
    await wait()

    return {
      rows: cloneValue(matrixRows),
      lookups: cloneValue(matrixLookups),
      summary: cloneValue(matrixSummary),
      loadedAt: new Date().toISOString(),
    }
  },
}
