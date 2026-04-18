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
  name: string
  path: string
  icon: LucideIcon
  description: string
}

export interface AppNavGroup {
  id: string
  label: string
  items: AppNavItem[]
}

export const appNavGroups: AppNavGroup[] = [
  {
    id: 'main',
    label: 'Main',
    items: [
      {
        id: 'home',
        name: 'Dashboard',
        path: '/',
        icon: LayoutDashboard,
        description: '首頁總覽',
      },
      {
        id: 'items',
        name: 'Items',
        path: '/items',
        icon: Package,
        description: '管理品項清單',
      },
    ],
  },
  {
    id: 'workflow',
    label: 'Workflow',
    items: [
      {
        id: 'bpmn-definitions',
        name: 'Processes',
        path: '/bpmn/definitions',
        icon: Workflow,
        description: '流程定義管理',
      },
      {
        id: 'bpmn-instances',
        name: 'Instances',
        path: '/bpmn/instances',
        icon: GitFork,
        description: '流程執行中實例',
      },
      {
        id: 'bpmn-tasks',
        name: 'My Tasks',
        path: '/bpmn/tasks',
        icon: ListTodo,
        description: '我的待辦任務',
      },
    ],
  },
  {
    id: 'procurement',
    label: '採購管理',
    items: [
      {
        id: 'procurement-plans',
        name: '採購計畫',
        path: '/procurement/plans',
        icon: ShoppingCart,
        description: '管理與送審採購計畫',
      },
    ],
  },
  {
    id: 'orders',
    label: '訂單管理',
    items: [
      {
        id: 'orders',
        name: '訂單列表',
        path: '/orders',
        icon: ClipboardList,
        description: '管理採購訂單',
      },
      {
        id: 'hold-summary',
        name: 'On-Hold 總覽',
        path: '/orders/holds',
        icon: PauseCircle,
        description: '查看 On-Hold 訂單彙整',
      },
    ],
  },
  {
    id: 'system',
    label: 'System',
    items: [
      {
        id: 'about',
        name: 'About',
        path: '/about',
        icon: Info,
        description: '關於此系統',
      },
    ],
  },
]
