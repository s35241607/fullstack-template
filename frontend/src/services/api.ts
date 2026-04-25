import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error.response?.data ?? error.message)
    return Promise.reject(error)
  },
)

// ── PO Management Types ───────────────────────────────────────────────────────

export interface PurchaseOrderReceipt {
  id: string
  receipt_number: string
  received_date: string
  received_quantity: number
}

export interface PurchaseOrderPullInRecord {
  id: string
  source_schedule_id: string
  created_schedule_id: string
  previous_commit_date: string
  target_date: string
  quantity: number
  note: string
  created_at: string
  created_by: string
}

export interface PurchaseOrderSchedule {
  id: string
  schedule_no: string
  commit_date: string
  quantity: number
  received_quantity: number
  origin: 'ORIGINAL' | 'PULL_IN'
  source_schedule_id: string | null
  receipts: PurchaseOrderReceipt[]
}

export interface PurchaseOrderLine {
  id: string
  line_number: string
  supplier_name: string
  item_code: string
  item_name: string
  order_date: string
  notes: string
  schedules: PurchaseOrderSchedule[]
  pull_in_records: PurchaseOrderPullInRecord[]
}

export interface PurchaseOrder {
  id: string
  order_number: string
  supplier_name: string
  supplier_code: string
  order_date: string
  buyer_name: string
  notes: string
  currency: string
  lines: PurchaseOrderLine[]
  canceled_at: string | null
}

export interface CreatePurchaseOrderPayload {
  order_number: string
  supplier_name: string
  supplier_code?: string
  order_date: string
  expected_delivery_date: string
  notes?: string
}

export interface ApplyPullInPayload {
  target_date: string
  quantity: number
  note?: string
  requested_by?: string
}

export interface UpdatePurchaseOrderSchedulePayload {
  commit_date: string
  quantity: number
}

export interface ModelHoldSummary {
  model_name: string
  total_on_hold_quantity: number
  locked_quantity: number
}

export interface ModelHoldDetail {
  id: string
  order_number: string
  model_name: string
  supplier_name: string
  hold_type: 'A' | 'B'
  available_quantity: number
  locked_by: string | null
}

const PO_STORAGE_KEY = 'frontend.po-management.orders.v1'

function makeId(prefix: string) {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return `${prefix}-${crypto.randomUUID()}`
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function cloneValue<T>(value: T): T {
  if (typeof structuredClone === 'function') {
    return structuredClone(value)
  }

  return JSON.parse(JSON.stringify(value)) as T
}

function wait(ms = 80) {
  return new Promise((resolve) => globalThis.setTimeout(resolve, ms))
}

function getOpenQuantity(schedule: PurchaseOrderSchedule) {
  return Math.max(schedule.quantity - schedule.received_quantity, 0)
}

function sortLineSchedules(line: PurchaseOrderLine) {
  line.schedules.sort((left, right) => left.commit_date.localeCompare(right.commit_date))
}

function seedPurchaseOrders(): PurchaseOrder[] {
  return [
    {
      id: 'po-2026-0001',
      order_number: 'PO-2026-0001',
      supplier_name: '多供應商整合單',
      supplier_code: 'MIXED',
      order_date: '2026-04-01',
      buyer_name: 'Kelly Lin',
      notes: '先進封裝 Header 採購批次',
      currency: 'TWD',
      canceled_at: null,
      lines: [
        {
          id: 'po-2026-0001-line-02',
          line_number: '02',
          supplier_name: '鴻海 (Foxconn)',
          item_code: 'IND-10UH',
          item_name: '高頻電感 10uH',
          order_date: '2026-04-01',
          notes: 'Header 主電源濾波料',
          schedules: [
            {
              id: 'po-2026-0001-line-02-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-16',
              quantity: 3598,
              received_quantity: 2631,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [
                {
                  id: 'rcv-1610',
                  receipt_number: 'RCV-1610',
                  received_date: '2026-04-15',
                  received_quantity: 2631,
                },
              ],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0001-line-03',
          line_number: '03',
          supplier_name: '日月光 (ASE)',
          item_code: 'MLCC-0402',
          item_name: 'MLCC 0402 被動元件',
          order_date: '2026-04-01',
          notes: '已先通知供應商備料',
          schedules: [
            {
              id: 'po-2026-0001-line-03-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-04',
              quantity: 1800,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
            {
              id: 'po-2026-0001-line-03-sch-p01',
              schedule_no: 'P01',
              commit_date: '2026-04-28',
              quantity: 600,
              received_quantity: 0,
              origin: 'PULL_IN',
              source_schedule_id: 'po-2026-0001-line-03-sch-01',
              receipts: [],
            },
          ],
          pull_in_records: [
            {
              id: 'pullin-2026-0001-03-01',
              source_schedule_id: 'po-2026-0001-line-03-sch-01',
              created_schedule_id: 'po-2026-0001-line-03-sch-p01',
              previous_commit_date: '2026-05-04',
              target_date: '2026-04-28',
              quantity: 600,
              note: '產線切換提前，先拉 600 pcs',
              created_at: '2026-04-10T09:30:00.000Z',
              created_by: 'Kelly Lin',
            },
          ],
        },
        {
          id: 'po-2026-0001-line-04',
          line_number: '04',
          supplier_name: '日月光 (ASE)',
          item_code: 'HSNK-AL',
          item_name: '散熱模組 (鋁心)',
          order_date: '2026-04-01',
          notes: '已全數到貨',
          schedules: [
            {
              id: 'po-2026-0001-line-04-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-01',
              quantity: 1800,
              received_quantity: 1800,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [
                {
                  id: 'rcv-1702',
                  receipt_number: 'RCV-1702',
                  received_date: '2026-04-12',
                  received_quantity: 1800,
                },
              ],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0001-line-05',
          line_number: '05',
          supplier_name: '德州儀器 (TI)',
          item_code: 'PMIC-8921',
          item_name: 'PMIC 電源管理晶片',
          order_date: '2026-04-01',
          notes: '供應商回覆 wafer slot 延後',
          schedules: [
            {
              id: 'po-2026-0001-line-05-sch-01',
              schedule_no: '01',
              commit_date: '2026-04-16',
              quantity: 960,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
      ],
    },
    {
      id: 'po-2026-0002',
      order_number: 'PO-2026-0002',
      supplier_name: '第二批採購',
      supplier_code: 'BATCH-2',
      order_date: '2026-04-01',
      buyer_name: 'Ryan Wu',
      notes: 'MCU / 被動件補貨',
      currency: 'TWD',
      canceled_at: null,
      lines: [
        {
          id: 'po-2026-0002-line-01',
          line_number: '01',
          supplier_name: '鴻海 (Foxconn)',
          item_code: 'MCU-32',
          item_name: 'MCU-32 微控制器',
          order_date: '2026-04-01',
          notes: '已提醒供應商提前生產',
          schedules: [
            {
              id: 'po-2026-0002-line-01-sch-01',
              schedule_no: '01',
              commit_date: '2026-04-26',
              quantity: 4200,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0002-line-02',
          line_number: '02',
          supplier_name: '台積電 (TSMC)',
          item_code: 'CAP-10UH',
          item_name: '高頻電感 10uH',
          order_date: '2026-04-01',
          notes: '已進站，等待分批收料',
          schedules: [
            {
              id: 'po-2026-0002-line-02-sch-01',
              schedule_no: '01',
              commit_date: '2026-04-13',
              quantity: 2400,
              received_quantity: 1200,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [
                {
                  id: 'rcv-1808',
                  receipt_number: 'RCV-1808',
                  received_date: '2026-04-14',
                  received_quantity: 1200,
                },
              ],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0002-line-03',
          line_number: '03',
          supplier_name: '鴻海 (Foxconn)',
          item_code: 'MLCC-0402-B',
          item_name: 'MLCC 0402 被動元件',
          order_date: '2026-04-01',
          notes: '第一波新到貨',
          schedules: [
            {
              id: 'po-2026-0002-line-03-sch-01',
              schedule_no: '01',
              commit_date: '2026-04-14',
              quantity: 3600,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0002-line-04',
          line_number: '04',
          supplier_name: '日月光 (ASE)',
          item_code: 'MLCC-0402-C',
          item_name: 'MLCC 0402 被動元件',
          order_date: '2026-04-01',
          notes: '供應商生產中',
          schedules: [
            {
              id: 'po-2026-0002-line-04-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-03',
              quantity: 2800,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
        {
          id: 'po-2026-0002-line-05',
          line_number: '05',
          supplier_name: '鴻海 (Foxconn)',
          item_code: 'RES-0402',
          item_name: 'MLCC 0402 被動元件',
          order_date: '2026-04-01',
          notes: '生產排程已確認',
          schedules: [
            {
              id: 'po-2026-0002-line-05-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-10',
              quantity: 3200,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
      ],
    },
    {
      id: 'po-2026-0003',
      order_number: 'PO-2026-0003',
      supplier_name: '第三批採購',
      supplier_code: 'BATCH-3',
      order_date: '2026-04-01',
      buyer_name: 'Ariel Chen',
      notes: 'Power IC 緊急交付',
      currency: 'TWD',
      canceled_at: null,
      lines: [
        {
          id: 'po-2026-0003-line-01',
          line_number: '01',
          supplier_name: '台積電 (TSMC)',
          item_code: 'PMIC-6001',
          item_name: 'PMIC 電源管理晶片',
          order_date: '2026-04-01',
          notes: '尚有一批可提前拉貨',
          schedules: [
            {
              id: 'po-2026-0003-line-01-sch-01',
              schedule_no: '01',
              commit_date: '2026-05-11',
              quantity: 5400,
              received_quantity: 0,
              origin: 'ORIGINAL',
              source_schedule_id: null,
              receipts: [],
            },
          ],
          pull_in_records: [],
        },
      ],
    },
  ]
}

function loadOrders() {
  if (typeof localStorage === 'undefined') {
    return cloneValue(seedPurchaseOrders())
  }

  const raw = localStorage.getItem(PO_STORAGE_KEY)
  if (!raw) {
    const seeded = seedPurchaseOrders()
    localStorage.setItem(PO_STORAGE_KEY, JSON.stringify(seeded))
    return cloneValue(seeded)
  }

  try {
    return cloneValue(JSON.parse(raw) as PurchaseOrder[])
  } catch {
    const seeded = seedPurchaseOrders()
    localStorage.setItem(PO_STORAGE_KEY, JSON.stringify(seeded))
    return cloneValue(seeded)
  }
}

function saveOrders(orders: PurchaseOrder[]) {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(PO_STORAGE_KEY, JSON.stringify(orders))
  }
}

function getOrderOrThrow(orders: PurchaseOrder[], orderId: string) {
  const order = orders.find((candidate) => candidate.id === orderId)
  if (!order) {
    throw new Error('Purchase order not found.')
  }

  return order
}

function getLineOrThrow(order: PurchaseOrder, lineId: string) {
  const line = order.lines.find((candidate) => candidate.id === lineId)
  if (!line) {
    throw new Error('Purchase order line not found.')
  }

  return line
}

function getScheduleOrThrow(line: PurchaseOrderLine, scheduleId: string) {
  const schedule = line.schedules.find((candidate) => candidate.id === scheduleId)
  if (!schedule) {
    throw new Error('Schedule not found.')
  }

  return schedule
}

export const ordersApi = {
  list: async () => {
    await wait()
    return loadOrders().sort((left, right) => left.order_number.localeCompare(right.order_number))
  },

  get: async (id: string) => {
    await wait()
    return getOrderOrThrow(loadOrders(), id)
  },

  create: async (data: CreatePurchaseOrderPayload) => {
    await wait()

    const orders = loadOrders()
    const order: PurchaseOrder = {
      id: makeId('po'),
      order_number: data.order_number,
      supplier_name: data.supplier_name,
      supplier_code: data.supplier_code ?? 'NEW',
      order_date: data.order_date,
      buyer_name: 'Planner Team',
      notes: data.notes ?? '',
      currency: 'TWD',
      lines: [],
      canceled_at: null,
    }

    orders.unshift(order)
    saveOrders(orders)
    return cloneValue(order)
  },

  delete: async (id: string) => {
    await wait()
    const orders = loadOrders().filter((order) => order.id !== id)
    saveOrders(orders)
  },

  cancel: async (id: string) => {
    await wait()
    const orders = loadOrders()
    const order = getOrderOrThrow(orders, id)
    order.canceled_at = new Date().toISOString()
    saveOrders(orders)
    return cloneValue(order)
  },

  updateSchedule: async (
    orderId: string,
    lineId: string,
    scheduleId: string,
    payload: UpdatePurchaseOrderSchedulePayload,
  ) => {
    await wait()

    const orders = loadOrders()
    const order = getOrderOrThrow(orders, orderId)
    const line = getLineOrThrow(order, lineId)
    const schedule = getScheduleOrThrow(line, scheduleId)

    if (!payload.commit_date) {
      throw new Error('Commit date is required.')
    }

    if (payload.quantity <= 0) {
      throw new Error('Schedule quantity must be greater than zero.')
    }

    if (payload.quantity < schedule.received_quantity) {
      throw new Error('Schedule quantity cannot be less than the received quantity.')
    }

    schedule.commit_date = payload.commit_date
    schedule.quantity = payload.quantity

    sortLineSchedules(line)
    saveOrders(orders)

    return cloneValue(order)
  },

  applyPullIn: async (
    orderId: string,
    lineId: string,
    scheduleId: string,
    payload: ApplyPullInPayload,
  ) => {
    await wait()

    const orders = loadOrders()
    const order = getOrderOrThrow(orders, orderId)
    const line = getLineOrThrow(order, lineId)
    const schedule = getScheduleOrThrow(line, scheduleId)
    const openQuantity = getOpenQuantity(schedule)

    if (payload.quantity <= 0) {
      throw new Error('Pull in quantity must be greater than zero.')
    }

    if (payload.quantity > openQuantity) {
      throw new Error('Pull in quantity cannot exceed the remaining open quantity.')
    }

    if (payload.target_date >= schedule.commit_date) {
      throw new Error('Target date must be earlier than the current commit date.')
    }

    const pullInId = makeId('pullin')
    const requestedBy = payload.requested_by?.trim() || 'Planner Team'
    const createdAt = new Date().toISOString()
    const previousCommitDate = schedule.commit_date
    let createdScheduleId = schedule.id

    if (payload.quantity === openQuantity && schedule.received_quantity === 0) {
      schedule.commit_date = payload.target_date
      schedule.origin = 'PULL_IN'
      schedule.source_schedule_id = schedule.source_schedule_id ?? schedule.id
    } else {
      schedule.quantity = schedule.received_quantity + (openQuantity - payload.quantity)

      const newSchedule: PurchaseOrderSchedule = {
        id: makeId('schedule'),
        schedule_no: `P${String(line.pull_in_records.length + 1).padStart(2, '0')}`,
        commit_date: payload.target_date,
        quantity: payload.quantity,
        received_quantity: 0,
        origin: 'PULL_IN',
        source_schedule_id: schedule.id,
        receipts: [],
      }

      createdScheduleId = newSchedule.id
      line.schedules.push(newSchedule)
    }

    line.pull_in_records.unshift({
      id: pullInId,
      source_schedule_id: schedule.id,
      created_schedule_id: createdScheduleId,
      previous_commit_date: previousCommitDate,
      target_date: payload.target_date,
      quantity: payload.quantity,
      note: payload.note?.trim() || '',
      created_at: createdAt,
      created_by: requestedBy,
    })

    sortLineSchedules(line)
    saveOrders(orders)

    return cloneValue(order)
  },

  holdSummary: async () => {
    await wait(40)

    const modelMap = new Map<string, ModelHoldSummary>()
    for (const order of loadOrders()) {
      for (const line of order.lines) {
        const openQuantity = line.schedules.reduce(
          (total, schedule) => total + getOpenQuantity(schedule),
          0,
        )
        const existing = modelMap.get(line.item_name)
        if (existing) {
          existing.total_on_hold_quantity += openQuantity
          existing.locked_quantity += line.pull_in_records.reduce(
            (total, record) => total + record.quantity,
            0,
          )
        } else {
          modelMap.set(line.item_name, {
            model_name: line.item_name,
            total_on_hold_quantity: openQuantity,
            locked_quantity: line.pull_in_records.reduce(
              (total, record) => total + record.quantity,
              0,
            ),
          })
        }
      }
    }

    return Array.from(modelMap.values())
  },

  holdsByModel: async (modelName: string) => {
    await wait(40)

    return loadOrders().flatMap((order) =>
      order.lines
        .filter((line) => line.item_name === modelName)
        .map<ModelHoldDetail>((line, index) => ({
          id: `${line.id}-hold-${index + 1}`,
          order_number: order.order_number,
          model_name: line.item_name,
          supplier_name: line.supplier_name,
          hold_type: index % 2 === 0 ? 'A' : 'B',
          available_quantity: line.schedules.reduce(
            (total, schedule) => total + getOpenQuantity(schedule),
            0,
          ),
          locked_by: line.pull_in_records[0]?.created_by ?? null,
        })),
    )
  },

  resetDemoData: async () => {
    await wait(40)
    const seeded = seedPurchaseOrders()
    saveOrders(seeded)
    return cloneValue(seeded)
  },
}
