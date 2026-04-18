const en = {
  lang: 'EN',

  nav: {
    groups: {
      main: 'Main',
      system: 'System',
    },
    items: {
      home: 'Dashboard',
      about: 'About',
    },
    desc: {
      home: 'Overview dashboard',
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
    title: 'Fullstack Template',
    subtitle: 'Vue 3 + TypeScript + FastAPI + SQLAlchemy',
    modules: 'Modules',
    moduleCards: {
      api: {
        title: 'API Documentation',
        desc: 'FastAPI auto-generated OpenAPI documentation',
      },
    },
  },

  sidebar: {
    appSubtitle: 'Enterprise Platform',
    copyright: '© 2026 Fullstack Template',
  },

  command: {
    title: 'Global search',
    description: 'Search pages and commands across the application.',
    placeholder: 'Search pages, commands (Ctrl+K)…',
    empty: 'No results found.',
    select: 'Select',
    go: 'Go',
    close: 'Close',
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
