import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { breadcrumb: 'Dashboard' },
    },
    {
      path: '/items',
      name: 'items',
      component: () => import('@/views/ItemsView.vue'),
      meta: { breadcrumb: 'Items' },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { breadcrumb: 'About' },
    },
    // BPMN Routes
    {
      path: '/bpmn',
      redirect: '/bpmn/definitions',
      meta: { breadcrumb: 'Workflow' },
    },
    {
      path: '/bpmn/definitions',
      name: 'bpmn-definitions',
      component: () => import('@/views/bpmn/ProcessDefinitionsView.vue'),
      meta: { breadcrumb: 'Processes' },
    },
    {
      path: '/bpmn/definitions/:id',
      name: 'bpmn-definition-detail',
      component: () => import('@/views/bpmn/ProcessDefinitionDetailView.vue'),
      meta: { breadcrumb: 'Process Detail' },
    },
    {
      path: '/bpmn/instances',
      name: 'bpmn-instances',
      component: () => import('@/views/bpmn/ProcessInstancesView.vue'),
      meta: { breadcrumb: 'Instances' },
    },
    {
      path: '/bpmn/tasks',
      name: 'bpmn-tasks',
      component: () => import('@/views/bpmn/MyTasksView.vue'),
      meta: { breadcrumb: 'My Tasks' },
    },
    // Procurement Routes
    {
      path: '/procurement',
      redirect: '/procurement/plans',
      meta: { breadcrumb: '採購管理' },
    },
    {
      path: '/procurement/plans',
      name: 'procurement-plans',
      component: () => import('@/views/procurement/ProcurementPlansView.vue'),
      meta: { breadcrumb: '採購計畫' },
    },
    {
      path: '/procurement/plans/:id',
      name: 'procurement-plan-detail',
      component: () => import('@/views/procurement/ProcurementPlanDetailView.vue'),
      meta: { breadcrumb: '計畫詳情' },
    },
    // Order Routes
    {
      path: '/orders',
      name: 'orders',
      component: () => import('@/views/orders/OrdersView.vue'),
      meta: { breadcrumb: '訂單管理' },
    },
    {
      path: '/orders/holds',
      name: 'hold-summary',
      component: () => import('@/views/orders/HoldSummaryView.vue'),
      meta: { breadcrumb: 'On-Hold 總覽' },
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      component: () => import('@/views/orders/OrderDetailView.vue'),
      meta: { breadcrumb: '訂單詳情' },
    },
  ],
})

export default router
