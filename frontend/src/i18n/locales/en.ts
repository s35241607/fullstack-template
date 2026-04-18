const en = {
  lang: 'EN',

  nav: {
    groups: {
      main: 'Main',
      workflow: 'Workflow',
      procurement: 'Procurement',
      orders: 'Orders',
      system: 'System',
    },
    items: {
      home: 'Dashboard',
      items: 'Items',
      bpmnDefinitions: 'Processes',
      bpmnDefinitionDetail: 'Process Detail',
      bpmnInstances: 'Instances',
      bpmnTasks: 'My Tasks',
      procurementPlans: 'Procurement Plans',
      procurementPlanDetail: 'Plan Detail',
      orders: 'Orders',
      orderDetail: 'Order Detail',
      holdSummary: 'On-Hold Summary',
      about: 'About',
    },
    desc: {
      home: 'Overview dashboard',
      items: 'Manage item catalog',
      bpmnDefinitions: 'Process definition management',
      bpmnInstances: 'Active process instances',
      bpmnTasks: 'My pending tasks',
      procurementPlans: 'Manage & submit procurement plans',
      orders: 'Manage purchase orders',
      holdSummary: 'View On-Hold order summary',
      about: 'About this system',
    },
  },

  header: {
    searchPlaceholder: 'Search…',
    searchTooltip: 'Search pages (Ctrl+K)',
    notificationsTooltip: 'Notifications',
    notificationsTitle: 'Notifications',
    themeTooltip: 'Theme & Appearance',
    accountTooltip: 'My Account',
    langTooltip: 'Switch Language',
    toggleSidebar: 'Toggle Sidebar',
    markAllRead: 'Mark all as read',
    noNotifications: 'No notifications yet',
    loading: 'Loading…',
    myAccount: 'My Account',
  },

  theme: {
    title: 'Personalization',
    subtitle: 'Customize the visual style of your application',
    primaryColor: 'Primary Color',
    surface: 'Surface Style',
    darkMode: 'Appearance',
    light: 'Light',
    dark: 'Dark',
    colors: {
      zinc: 'Zinc',
      blue: 'Blue',
      violet: 'Violet',
      rose: 'Rose',
      orange: 'Orange',
      green: 'Green',
    },
    surfaces: {
      zinc: 'Zinc',
      slate: 'Slate',
      gray: 'Gray',
      neutral: 'Neutral',
      stone: 'Stone',
    },
  },

  home: {
    title: 'Enterprise Procurement System',
    subtitle: 'Order Tracking · On-Hold Management · Procurement Approval',
    stats: {
      orders: 'Active Orders',
      holds: 'Hold Quantity',
      plans: 'Procurement Plans',
    },
    modules: 'Modules',
    moduleCards: {
      orders: {
        title: 'Order Management',
        desc: 'View all purchase orders, item details, receipt records and delivery tracking',
      },
      holds: {
        title: 'On-Hold Overview',
        desc: 'Summarize hold quantities by model, quickly grasp hold status',
      },
      procurement: {
        title: 'Procurement Plans',
        desc: 'Create and manage procurement plans with full approval workflow',
      },
      api: {
        title: 'API Documentation',
        desc: 'FastAPI auto-generated OpenAPI documentation',
      },
    },
  },

  sidebar: {
    appSubtitle: 'Enterprise Platform',
    copyright: '© 2026 Lan Side Project',
  },

  command: {
    placeholder: 'Search pages, commands (Ctrl+K)…',
    empty: 'No results found.',
  },

  common: {
    loading: 'Loading…',
    profile: 'Profile',
    settings: 'Settings',
    logout: 'Log out',
  },

  toast: {
    refreshing: 'Refreshing…',
    deleteSuccess: 'Deleted successfully',
    cancelSuccess: 'Cancelled successfully',
    createSuccess: 'Created successfully',
    updateSuccess: 'Updated successfully',
    error: 'Operation failed',
    saveSuccess: 'Saved successfully',
  },
}

export default en
export type MessageSchema = typeof en
