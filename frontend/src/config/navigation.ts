import {
  ClipboardList,
  GitFork,
  Info,
  LayoutDashboard,
  ListTodo,
  Package,
  PauseCircle,
  ShoppingCart,
  Workflow,
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
        id: 'items',
        name: 'nav.items.items',
        path: '/items',
        icon: Package,
        description: 'nav.desc.items',
      },
    ],
  },
  {
    id: 'workflow',
    label: 'nav.groups.workflow',
    items: [
      {
        id: 'bpmn-definitions',
        name: 'nav.items.bpmnDefinitions',
        path: '/bpmn/definitions',
        icon: Workflow,
        description: 'nav.desc.bpmnDefinitions',
      },
      {
        id: 'bpmn-instances',
        name: 'nav.items.bpmnInstances',
        path: '/bpmn/instances',
        icon: GitFork,
        description: 'nav.desc.bpmnInstances',
      },
      {
        id: 'bpmn-tasks',
        name: 'nav.items.bpmnTasks',
        path: '/bpmn/tasks',
        icon: ListTodo,
        description: 'nav.desc.bpmnTasks',
      },
    ],
  },
  {
    id: 'procurement',
    label: 'nav.groups.procurement',
    items: [
      {
        id: 'procurement-plans',
        name: 'nav.items.procurementPlans',
        path: '/procurement/plans',
        icon: ShoppingCart,
        description: 'nav.desc.procurementPlans',
      },
    ],
  },
  {
    id: 'orders',
    label: 'nav.groups.orders',
    items: [
      {
        id: 'orders',
        name: 'nav.items.orders',
        path: '/orders',
        icon: ClipboardList,
        description: 'nav.desc.orders',
      },
      {
        id: 'hold-summary',
        name: 'nav.items.holdSummary',
        path: '/orders/holds',
        icon: PauseCircle,
        description: 'nav.desc.holdSummary',
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
