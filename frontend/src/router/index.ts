import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { breadcrumb: 'nav.items.home' },
    },
    {
      path: '/items',
      name: 'items',
      component: () => import('@/views/ItemsView.vue'),
      meta: { breadcrumb: 'nav.items.items' },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { breadcrumb: 'nav.items.about' },
    },
    // BPMN Routes
    {
      path: '/bpmn',
      redirect: '/bpmn/definitions',
      meta: { breadcrumb: 'nav.groups.workflow' },
    },
    {
      path: '/bpmn/definitions',
      name: 'bpmn-definitions',
      component: () => import('@/views/bpmn/ProcessDefinitionsView.vue'),
      meta: { breadcrumb: 'nav.items.bpmnDefinitions' },
    },
    {
      path: '/bpmn/definitions/:id',
      name: 'bpmn-definition-detail',
      component: () => import('@/views/bpmn/ProcessDefinitionDetailView.vue'),
      meta: { breadcrumb: 'nav.items.bpmnDefinitionDetail' },
    },
    {
      path: '/bpmn/instances',
      name: 'bpmn-instances',
      component: () => import('@/views/bpmn/ProcessInstancesView.vue'),
      meta: { breadcrumb: 'nav.items.bpmnInstances' },
    },
    {
      path: '/bpmn/tasks',
      name: 'bpmn-tasks',
      component: () => import('@/views/bpmn/MyTasksView.vue'),
      meta: { breadcrumb: 'nav.items.bpmnTasks' },
    },
    // Procurement Routes
    {
      path: '/procurement',
      redirect: '/procurement/plans',
      meta: { breadcrumb: 'nav.groups.procurement' },
    },
    {
      path: '/procurement/plans',
      name: 'procurement-plans',
      component: () => import('@/views/procurement/ProcurementPlansView.vue'),
      meta: { breadcrumb: 'nav.items.procurementPlans' },
    },
    {
      path: '/procurement/plans/:id',
      name: 'procurement-plan-detail',
      component: () => import('@/views/procurement/ProcurementPlanDetailView.vue'),
      meta: { breadcrumb: 'nav.items.procurementPlanDetail' },
    },
    // Order Routes
    {
      path: '/orders',
      name: 'orders',
      component: () => import('@/views/orders/OrdersView.vue'),
      meta: { breadcrumb: 'nav.items.orders' },
    },
    {
      path: '/orders/holds',
      name: 'hold-summary',
      component: () => import('@/views/orders/HoldSummaryView.vue'),
      meta: { breadcrumb: 'nav.items.holdSummary' },
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      component: () => import('@/views/orders/OrderDetailView.vue'),
      meta: { breadcrumb: 'nav.items.orderDetail' },
    },
  ],
})

export default router
