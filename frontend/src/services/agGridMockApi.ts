export type InventoryLookupKey = 'categories' | 'statuses' | 'suppliers' | 'warehouses'

export type InventorySortDirection = 'asc' | 'desc'

export interface InventoryRow extends Record<string, unknown> {
  id: string
  itemCode: string
  itemName: string
  category: string
  supplier: string
  warehouse: string
  status: string
  stock: number
  reserved: number
  unitPrice: number
  buyer: string
  lastUpdate: string
}

export interface InventorySortModelItem {
  colId: string
  sort: InventorySortDirection
  sortIndex?: number | null
}

export interface InventoryFilterItem {
  filterType?: string
  type?: string
  filter?: unknown
  filterTo?: unknown
  values?: string[]
  operator?: 'AND' | 'OR'
  conditions?: InventoryFilterItem[]
}

export type InventoryFilterModel = Record<string, InventoryFilterItem>

export interface InventoryDropdownFilters {
  category?: string
  supplier?: string
  status?: string
  warehouse?: string
}

export interface InventoryQueryParams {
  page: number
  pageSize: number
  quickSearch?: string
  sortModel?: InventorySortModelItem[]
  filterModel?: InventoryFilterModel
  dropdownFilters?: InventoryDropdownFilters
}

export interface InventoryQueryResult {
  rows: InventoryRow[]
  total: number
  page: number
  pageSize: number
}

export type InventoryLookupOptions = Record<InventoryLookupKey, string[]>

const categories = ['IC', '被動元件', '機構件', '連接器', '光電', '電源模組']
const statuses = ['可用', '低庫存', '待補貨', '鎖定', '驗收中']
const suppliers = [
  '台積電 (TSMC)',
  '日月光 (ASE)',
  '鴻海 (Foxconn)',
  '德州儀器 (TI)',
  '村田 (Murata)',
  '億光 (Everlight)',
]
const warehouses = ['W-A1', 'W-A2', 'W-B1', 'W-C3', 'W-D1']
const buyers = ['Kelly Lin', 'Ryan Wu', 'Ariel Chen', 'Mina Hsu']
const itemNames = [
  'PMIC 電源管理晶片',
  'MLCC 0402 電容',
  '高頻電感 10uH',
  'USB-C 連接器',
  '散熱模組 (鋁心)',
  '石英振盪器 24MHz',
  'LED 指示燈',
  'MCU-32 微控制器',
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

function formatDate(dayOffset: number) {
  const date = new Date(Date.UTC(2026, 3, 1 + dayOffset))
  return date.toISOString().slice(0, 10)
}

function buildInventoryRows(): InventoryRow[] {
  return Array.from({ length: 136 }, (_, index) => {
    const category = categories[index % categories.length]
    const stock = 120 + ((index * 421) % 18500)
    const reserved = (index * 97) % Math.max(Math.floor(stock * 0.45), 1)
    const status =
      stock < 900 ? statuses[1] : index % 11 === 0 ? statuses[3] : index % 7 === 0 ? statuses[4] : statuses[0]

    return {
      id: `INV-${String(index + 1).padStart(4, '0')}`,
      itemCode: `${category.replace(/[^\dA-Z]/gi, '').slice(0, 4).toUpperCase() || 'MAT'}-${String(
        1000 + index,
      )}`,
      itemName: itemNames[index % itemNames.length],
      category,
      supplier: suppliers[(index * 3) % suppliers.length],
      warehouse: warehouses[(index * 5 + 2) % warehouses.length],
      status: index % 13 === 0 ? statuses[2] : status,
      stock,
      reserved,
      unitPrice: Number((1.2 + ((index * 17) % 900) / 10).toFixed(2)),
      buyer: buyers[(index * 2) % buyers.length],
      lastUpdate: formatDate((index * 3) % 45),
    }
  })
}

const inventoryRows = buildInventoryRows()

function getComparableValue(row: InventoryRow, colId: string) {
  return row[colId]
}

function includesText(value: unknown, query: string) {
  return String(value ?? '').toLowerCase().includes(query)
}

function matchesTextFilter(value: unknown, filter: InventoryFilterItem) {
  const source = String(value ?? '').toLowerCase()
  const target = String(filter.filter ?? '').toLowerCase()
  const type = filter.type ?? 'contains'

  if (type === 'blank') return source.length === 0
  if (type === 'notBlank') return source.length > 0
  if (!target) return true
  if (type === 'equals') return source === target
  if (type === 'notEqual') return source !== target
  if (type === 'startsWith') return source.startsWith(target)
  if (type === 'endsWith') return source.endsWith(target)
  if (type === 'notContains') return !source.includes(target)

  return source.includes(target)
}

function matchesNumberFilter(value: unknown, filter: InventoryFilterItem) {
  const source = Number(value)
  const target = Number(filter.filter)
  const targetTo = Number(filter.filterTo)
  const type = filter.type ?? 'equals'

  if (type === 'blank') return value === null || value === undefined || value === ''
  if (type === 'notBlank') return value !== null && value !== undefined && value !== ''
  if (Number.isNaN(source) || Number.isNaN(target)) return true
  if (type === 'notEqual') return source !== target
  if (type === 'lessThan') return source < target
  if (type === 'lessThanOrEqual') return source <= target
  if (type === 'greaterThan') return source > target
  if (type === 'greaterThanOrEqual') return source >= target
  if (type === 'inRange') return !Number.isNaN(targetTo) && source >= target && source <= targetTo

  return source === target
}

function matchesFilter(value: unknown, filter: InventoryFilterItem): boolean {
  if (Array.isArray(filter.conditions) && filter.conditions.length > 0) {
    const matcher = (condition: InventoryFilterItem) => matchesFilter(value, condition)
    return filter.operator === 'OR'
      ? filter.conditions.some(matcher)
      : filter.conditions.every(matcher)
  }

  if (filter.filterType === 'set' && filter.values?.length) {
    return filter.values.includes(String(value ?? ''))
  }

  if (filter.filterType === 'number') {
    return matchesNumberFilter(value, filter)
  }

  return matchesTextFilter(value, filter)
}

function applyGridFilters(rows: InventoryRow[], filterModel: InventoryFilterModel = {}) {
  const filterEntries = Object.entries(filterModel)
  if (filterEntries.length === 0) return rows

  return rows.filter((row) =>
    filterEntries.every(([colId, filter]) => matchesFilter(getComparableValue(row, colId), filter)),
  )
}

function applyDropdownFilters(rows: InventoryRow[], filters: InventoryDropdownFilters = {}) {
  return rows.filter((row) => {
    if (filters.category && filters.category !== 'all' && row.category !== filters.category) return false
    if (filters.supplier && filters.supplier !== 'all' && row.supplier !== filters.supplier) return false
    if (filters.status && filters.status !== 'all' && row.status !== filters.status) return false
    if (filters.warehouse && filters.warehouse !== 'all' && row.warehouse !== filters.warehouse) {
      return false
    }

    return true
  })
}

function applyQuickSearch(rows: InventoryRow[], quickSearch = '') {
  const query = quickSearch.trim().toLowerCase()
  if (!query) return rows

  return rows.filter((row) =>
    [row.id, row.itemCode, row.itemName, row.category, row.supplier, row.warehouse, row.status].some(
      (value) => includesText(value, query),
    ),
  )
}

function compareValues(left: unknown, right: unknown) {
  if (typeof left === 'number' && typeof right === 'number') {
    return left - right
  }

  return String(left ?? '').localeCompare(String(right ?? ''), 'zh-Hant', {
    numeric: true,
    sensitivity: 'base',
  })
}

function applySorting(rows: InventoryRow[], sortModel: InventorySortModelItem[] = []) {
  const activeSorts = sortModel
    .filter((sort) => sort.sort === 'asc' || sort.sort === 'desc')
    .sort((left, right) => (left.sortIndex ?? 0) - (right.sortIndex ?? 0))

  if (activeSorts.length === 0) return rows

  return [...rows].sort((left, right) => {
    for (const sort of activeSorts) {
      const result = compareValues(getComparableValue(left, sort.colId), getComparableValue(right, sort.colId))
      if (result !== 0) return sort.sort === 'asc' ? result : -result
    }

    return 0
  })
}

function uniqueSorted(values: string[], search = '') {
  const query = search.trim().toLowerCase()
  return Array.from(new Set(values))
    .filter((value) => !query || value.toLowerCase().includes(query))
    .sort((left, right) => left.localeCompare(right, 'zh-Hant'))
}

export const agGridMockApi = {
  queryInventory: async (params: InventoryQueryParams): Promise<InventoryQueryResult> => {
    await wait()

    const pageSize = Math.max(params.pageSize, 1)
    const filteredRows = applyGridFilters(
      applyDropdownFilters(applyQuickSearch(inventoryRows, params.quickSearch), params.dropdownFilters),
      params.filterModel,
    )
    const sortedRows = applySorting(filteredRows, params.sortModel)
    const total = sortedRows.length
    const totalPages = Math.max(Math.ceil(total / pageSize), 1)
    const page = Math.min(Math.max(params.page, 1), totalPages)
    const start = (page - 1) * pageSize

    return {
      rows: cloneValue(sortedRows.slice(start, start + pageSize)),
      total,
      page,
      pageSize,
    }
  },

  getLookupOptions: async (search = ''): Promise<InventoryLookupOptions> => {
    await wait(120)

    return {
      categories: uniqueSorted(inventoryRows.map((row) => row.category), search),
      statuses: uniqueSorted(inventoryRows.map((row) => row.status), search),
      suppliers: uniqueSorted(inventoryRows.map((row) => row.supplier), search),
      warehouses: uniqueSorted(inventoryRows.map((row) => row.warehouse), search),
    }
  },
}
