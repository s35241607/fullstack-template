import { h } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const PassThrough = { render: () => h(RouterView) }

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
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { breadcrumb: 'nav.items.about' },
    },
    {
      path: '/po-management',
      component: PassThrough,
      meta: { breadcrumb: 'nav.items.poManagement' },
      children: [
        {
          path: '',
          name: 'po-management',
          component: () => import('@/views/orders/PoManagementView.vue'),
        },
        {
          path: ':orderId',
          component: PassThrough,
          meta: { breadcrumbParam: 'orderId' },
          children: [
            {
              path: '',
              name: 'po-detail',
              component: () => import('@/views/orders/PoDetailView.vue'),
            },
            {
              path: 'lines/:lineId',
              name: 'po-line-detail',
              component: () => import('@/views/orders/PoLineDetailView.vue'),
              meta: { breadcrumbParam: 'lineId', breadcrumbPrefix: 'poDetail.linePrefix' },
            },
          ],
        },
      ],
    },
    {
      path: '/ag-grid-demo',
      name: 'ag-grid-demo',
      component: () => import('@/views/AgGridDemoView.vue'),
      meta: { breadcrumb: 'AG Grid 展示' },
    },
    {
      path: '/ag-grid-api-demo',
      name: 'ag-grid-api-demo',
      component: () => import('@/views/AgGridApiDemoView.vue'),
      meta: { breadcrumb: 'AG Grid API 展示' },
    },
    {
      path: '/ag-grid-po-receipt-pivot',
      name: 'ag-grid-po-receipt-pivot',
      component: () => import('@/views/AgGridPoReceiptPivotView.vue'),
      meta: { breadcrumb: 'nav.items.agGridPoReceiptPivot' },
    },
    {
      path: '/demo',
      name: 'demo',
      component: () => import('@/views/DemoView.vue'),
      meta: { breadcrumb: 'Demo Component 展示' },
    },
  ],
})

export default router
