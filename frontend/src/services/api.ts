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

export interface Item {
  id: string
  name: string
  description: string
}

export const itemsApi = {
  list: () => apiClient.get<Item[]>('/items/').then((r) => r.data),
  get: (id: string) => apiClient.get<Item>(`/items/${id}`).then((r) => r.data),
  create: (data: { name: string; description?: string }) =>
    apiClient.post<Item>('/items/', data).then((r) => r.data),
  update: (id: string, data: { name?: string; description?: string }) =>
    apiClient.patch<Item>(`/items/${id}`, data).then((r) => r.data),
  delete: (id: string) => apiClient.delete(`/items/${id}`),
}

// ── BPMN Types ─────────────────────────────────────────────────────────────────

export interface TaskDefinition {
  id: string
  process_definition_id: string
  name: string
  task_type: string
  position_x: number
  position_y: number
  config: Record<string, unknown>
}

export interface TransitionDefinition {
  id: string
  process_definition_id: string
  source_task_id: string
  target_task_id: string
  label: string
  condition: string
}

export interface ProcessDefinition {
  id: string
  name: string
  description: string
  version: number
  is_active: boolean
  created_at: string
  updated_at: string
  tasks: TaskDefinition[]
  transitions: TransitionDefinition[]
}

export interface TaskInstance {
  id: string
  process_instance_id: string
  task_definition_id: string
  task_name: string
  task_type: string
  status: string
  assignee: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  form_data: Record<string, unknown>
}

export interface ProcessInstance {
  id: string
  process_definition_id: string
  name: string
  status: string
  started_by: string
  started_at: string
  completed_at: string | null
  variables: Record<string, unknown>
  notes: string
  definition_name: string
  task_instances: TaskInstance[]
}

export interface ActiveTask {
  id: string
  process_instance_id: string
  task_definition_id: string
  task_name: string
  task_type: string
  status: string
  assignee: string
  created_at: string
  started_at: string | null
}

// ── BPMN API ───────────────────────────────────────────────────────────────────

export const bpmnApi = {
  // Process Definitions
  listDefinitions: () =>
    apiClient.get<ProcessDefinition[]>('/bpmn/definitions').then((r) => r.data),

  createDefinition: (data: { name: string; description?: string }) =>
    apiClient.post<ProcessDefinition>('/bpmn/definitions', data).then((r) => r.data),

  getDefinition: (id: string) =>
    apiClient.get<ProcessDefinition>(`/bpmn/definitions/${id}`).then((r) => r.data),

  updateDefinition: (
    id: string,
    data: { name?: string; description?: string; is_active?: boolean },
  ) => apiClient.patch<ProcessDefinition>(`/bpmn/definitions/${id}`, data).then((r) => r.data),

  deleteDefinition: (id: string) => apiClient.delete(`/bpmn/definitions/${id}`),

  addTask: (
    definitionId: string,
    data: {
      name: string
      task_type: string
      position_x?: number
      position_y?: number
      config?: Record<string, unknown>
    },
  ) =>
    apiClient
      .post<TaskDefinition>(`/bpmn/definitions/${definitionId}/tasks`, data)
      .then((r) => r.data),

  addTransition: (
    definitionId: string,
    data: {
      source_task_id: string
      target_task_id: string
      label?: string
      condition?: string
    },
  ) =>
    apiClient
      .post<TransitionDefinition>(`/bpmn/definitions/${definitionId}/transitions`, data)
      .then((r) => r.data),

  // Process Instances
  startProcess: (
    definitionId: string,
    data: { name: string; started_by?: string; variables?: Record<string, unknown> },
  ) =>
    apiClient
      .post<ProcessInstance>(`/bpmn/definitions/${definitionId}/start`, data)
      .then((r) => r.data),

  listInstances: (status?: string) =>
    apiClient
      .get<ProcessInstance[]>('/bpmn/instances', { params: { status_filter: status } })
      .then((r) => r.data),

  getInstance: (id: string) =>
    apiClient.get<ProcessInstance>(`/bpmn/instances/${id}`).then((r) => r.data),

  completeTask: (
    instanceId: string,
    taskId: string,
    data?: { form_data?: Record<string, unknown>; assignee?: string },
  ) =>
    apiClient
      .post<ProcessInstance>(`/bpmn/instances/${instanceId}/tasks/${taskId}/complete`, data ?? {})
      .then((r) => r.data),

  cancelInstance: (instanceId: string) =>
    apiClient.post<ProcessInstance>(`/bpmn/instances/${instanceId}/cancel`).then((r) => r.data),

  // Active tasks
  listActiveTasks: (assignee?: string) =>
    apiClient.get<ActiveTask[]>('/bpmn/tasks/active', { params: { assignee } }).then((r) => r.data),
}

// ── Order Types ─────────────────────────────────────────────────────────────────

export interface ReceivingRecord {
  id: string
  received_quantity: number
  received_date: string
  inspector: string
  note: string
}

export interface OrderHold {
  id: string
  hold_quantity: number
  reason: string
  held_by: string
  status: string
  created_at: string
  released_at: string | null
  released_by: string | null
}

export interface OrderItem {
  id: string
  item_number: number
  material_name: string
  model_name: string
  specification: string
  quantity: number
  unit_price: number
  delivery_date: string | null
  status: string
  received_quantity: number
  active_hold_quantity: number
  subtotal: number
  receiving_records: ReceivingRecord[]
  holds: OrderHold[]
}

export interface PurchaseOrder {
  id: string
  order_number: string
  supplier_name: string
  supplier_code: string
  order_date: string
  expected_delivery_date: string
  notes: string
  status: string
  total_amount: number
  total_ordered: number
  total_received: number
  created_at: string
  updated_at: string
  items: OrderItem[]
}

export interface ModelHoldSummary {
  model_name: string
  total_hold_quantity: number
  hold_count: number
}

export interface ModelHoldDetail {
  hold_id: string
  hold_quantity: number
  reason: string
  held_by: string
  created_at: string
  material_name: string
  model_name: string
  ordered_quantity: number
  order_number: string
  supplier_name: string
}

// ── Order API ──────────────────────────────────────────────────────────────────

export const ordersApi = {
  list: (status?: string) =>
    apiClient
      .get<PurchaseOrder[]>('/orders/', { params: status ? { status } : undefined })
      .then((r) => r.data),

  get: (id: string) => apiClient.get<PurchaseOrder>(`/orders/${id}`).then((r) => r.data),

  create: (data: {
    order_number: string
    supplier_name: string
    supplier_code?: string
    order_date: string
    expected_delivery_date: string
    notes?: string
  }) => apiClient.post<PurchaseOrder>('/orders/', data).then((r) => r.data),

  update: (
    id: string,
    data: { supplier_name?: string; expected_delivery_date?: string; notes?: string },
  ) => apiClient.patch<PurchaseOrder>(`/orders/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/orders/${id}`),

  cancel: (id: string) => apiClient.post<PurchaseOrder>(`/orders/${id}/cancel`).then((r) => r.data),

  close: (id: string) => apiClient.post<PurchaseOrder>(`/orders/${id}/close`).then((r) => r.data),

  addItem: (
    orderId: string,
    data: {
      item_number: number
      material_name: string
      model_name?: string
      specification?: string
      quantity?: number
      unit_price?: number
      delivery_date?: string
    },
  ) => apiClient.post<OrderItem>(`/orders/${orderId}/items`, data).then((r) => r.data),

  updateItem: (
    orderId: string,
    itemId: string,
    data: {
      material_name?: string
      model_name?: string
      specification?: string
      quantity?: number
      unit_price?: number
      delivery_date?: string
    },
  ) => apiClient.patch<OrderItem>(`/orders/${orderId}/items/${itemId}`, data).then((r) => r.data),

  addReceiving: (
    orderId: string,
    itemId: string,
    data: {
      received_quantity: number
      received_date: string
      inspector?: string
      note?: string
    },
  ) =>
    apiClient
      .post<ReceivingRecord>(`/orders/${orderId}/items/${itemId}/receiving`, data)
      .then((r) => r.data),

  addHold: (
    orderId: string,
    itemId: string,
    data: { hold_quantity: number; reason: string; held_by: string },
  ) =>
    apiClient.post<OrderHold>(`/orders/${orderId}/items/${itemId}/holds`, data).then((r) => r.data),

  releaseHold: (orderId: string, itemId: string, holdId: string, released_by: string) =>
    apiClient.post(`/orders/${orderId}/items/${itemId}/holds/${holdId}/release`, { released_by }),

  holdSummary: () => apiClient.get<ModelHoldSummary[]>('/orders/hold-summary').then((r) => r.data),

  holdsByModel: (modelName: string) =>
    apiClient
      .get<ModelHoldDetail[]>(`/orders/holds-by-model/${encodeURIComponent(modelName)}`)
      .then((r) => r.data),
}

// ── Procurement Types ──────────────────────────────────────────────────────────

export interface PlanItem {
  id: string
  equipment_name: string
  specification: string
  quantity: number
  estimated_unit_price: number
  note: string
  item_status: string
  spec_file_url: string | null
  spec_uploaded_by: string | null
  spec_uploaded_at: string | null
  supplier_name: string | null
  quoted_unit_price: number | null
  quoted_at: string | null
  subtotal: number
  final_subtotal: number
}

export interface ProcurementPlan {
  id: string
  name: string
  planned_date: string
  status: string
  total_amount: number
  items: PlanItem[]
}

// ── Procurement API ────────────────────────────────────────────────────────────

export const procurementApi = {
  listPlans: () => apiClient.get<ProcurementPlan[]>('/procurement-plans/').then((r) => r.data),

  getPlan: (id: string) =>
    apiClient.get<ProcurementPlan>(`/procurement-plans/${id}`).then((r) => r.data),

  createPlan: (data: { name: string; planned_date: string }) =>
    apiClient.post<ProcurementPlan>('/procurement-plans/', data).then((r) => r.data),

  updatePlan: (id: string, data: { name?: string; planned_date?: string }) =>
    apiClient.patch<ProcurementPlan>(`/procurement-plans/${id}`, data).then((r) => r.data),

  deletePlan: (id: string) => apiClient.delete(`/procurement-plans/${id}`),

  submitPlan: (id: string) =>
    apiClient.post<ProcurementPlan>(`/procurement-plans/${id}/submit`).then((r) => r.data),

  addItem: (
    planId: string,
    data: {
      equipment_name: string
      specification?: string
      quantity?: number
      estimated_unit_price?: number
      note?: string
    },
  ) => apiClient.post<PlanItem>(`/procurement-plans/${planId}/items`, data).then((r) => r.data),

  updateItem: (
    planId: string,
    itemId: string,
    data: {
      equipment_name?: string
      specification?: string
      quantity?: number
      estimated_unit_price?: number
      note?: string
    },
  ) =>
    apiClient
      .patch<PlanItem>(`/procurement-plans/${planId}/items/${itemId}`, data)
      .then((r) => r.data),

  removeItem: (planId: string, itemId: string) =>
    apiClient.delete(`/procurement-plans/${planId}/items/${itemId}`),

  // Workflow
  sendToEeReview: (id: string) =>
    apiClient.post<ProcurementPlan>(`/procurement-plans/${id}/ee-review`).then((r) => r.data),

  markQuoted: (id: string) =>
    apiClient.post<ProcurementPlan>(`/procurement-plans/${id}/mark-quoted`).then((r) => r.data),

  approvePlan: (id: string) =>
    apiClient.post<ProcurementPlan>(`/procurement-plans/${id}/approve`).then((r) => r.data),

  submitToBudget: (id: string) =>
    apiClient.post<ProcurementPlan>(`/procurement-plans/${id}/submit-budget`).then((r) => r.data),

  // Item SPEC / Quote
  uploadSpec: (planId: string, itemId: string, data: { file_url: string; uploaded_by: string }) =>
    apiClient
      .post<PlanItem>(`/procurement-plans/${planId}/items/${itemId}/upload-spec`, data)
      .then((r) => r.data),

  setQuote: (
    planId: string,
    itemId: string,
    data: { quoted_unit_price: number; supplier_name: string },
  ) =>
    apiClient
      .post<PlanItem>(`/procurement-plans/${planId}/items/${itemId}/set-quote`, data)
      .then((r) => r.data),
}

// ── Notification Types ─────────────────────────────────────────────────────────

export interface Notification {
  id: string
  title: string
  message: string
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'
  is_read: boolean
  link: string | null
  created_at: string
}

export interface UnreadCount {
  count: number
}

// ── Notification API ───────────────────────────────────────────────────────────

export const notificationsApi = {
  list: (unreadOnly = false) =>
    apiClient
      .get<Notification[]>('/notifications/', { params: { unread_only: unreadOnly } })
      .then((r) => r.data),

  unreadCount: () => apiClient.get<UnreadCount>('/notifications/unread-count').then((r) => r.data),

  markRead: (id: string) =>
    apiClient.patch<Notification>(`/notifications/${id}/read`).then((r) => r.data),

  markAllRead: () => apiClient.post('/notifications/read-all'),
}
