import {
  Database,
  Info,
  LayoutDashboard,
  PackageSearch,
  Shapes,
  Grid,
  type LucideIcon,
} from 'lucide-vue-next'

export interface AppNavItem {
  id: string
  /** i18n key — pass to $t() or t() in templates */
  name: string
  path: string
  icon: LucideIcon
  /** i18n key — pass to $t() or t() in templates */
  description: string
}

export interface AppNavGroup {
  id: string
  /** i18n key — pass to $t() or t() in templates */
  label: string
  items: AppNavItem[]
}

export const appNavGroups: AppNavGroup[] = [
  {
    id: 'main',
    label: 'nav.groups.main',
    items: [
      {
        id: 'home',
        name: 'nav.items.home',
        path: '/',
        icon: LayoutDashboard,
        description: 'nav.desc.home',
      },
      {
        id: 'po-management',
        name: 'nav.items.poManagement',
        path: '/po-management',
        icon: PackageSearch,
        description: 'nav.desc.poManagement',
      },
    ],
  },
  {
    id: 'system',
    label: 'nav.groups.system',
    items: [
      {
        id: 'about',
        name: 'nav.items.about',
        path: '/about',
        icon: Info,
        description: 'nav.desc.about',
      },
      {
        id: 'ag-grid-demo',
        name: 'AG Grid 展示',
        path: '/ag-grid-demo',
        icon: Grid,
        description: 'AG Grid 整合與功能展示',
      },
      {
        id: 'ag-grid-api-demo',
        name: 'AG Grid API 展示',
        path: '/ag-grid-api-demo',
        icon: Database,
        description: 'AG Grid 分頁查詢與動態下拉展示',
      },
      {
        id: 'demo',
        name: 'Demo 展示',
        path: '/demo',
        icon: Shapes,
        description: '共用元件展示頁面',
      },
    ],
  },
]
