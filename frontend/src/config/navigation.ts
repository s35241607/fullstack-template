import { Info, LayoutDashboard, PackageSearch, type LucideIcon } from 'lucide-vue-next'

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
    ],
  },
]
