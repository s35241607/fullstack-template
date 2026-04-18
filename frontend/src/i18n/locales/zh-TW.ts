import type { MessageSchema } from './en'

const zhTW: MessageSchema = {
  lang: '中文',

  nav: {
    groups: {
      main: '主要',
      system: '系統',
    },
    items: {
      home: '儀表板',
      about: '關於',
    },
    desc: {
      home: '首頁總覽',
      about: '關於此系統',
    },
  },

  header: {
    searchPlaceholder: '搜尋…',
    searchTooltip: '搜尋頁面 (Ctrl+K)',
    notificationsTooltip: '通知中心',
    notificationsTitle: '通知',
    themeTooltip: '配色方案與外觀切換',
    accountTooltip: '我的帳號',
    langTooltip: '切換語言',
    toggleSidebar: '收起/展開側邊欄',
    markAllRead: '全部已讀',
    noNotifications: '目前沒有通知',
    loading: '載入中…',
    myAccount: '我的帳號',
  },

  theme: {
    title: '個性化設定',
    subtitle: '自定義您的應用程式視覺風格',
    primaryColor: '主色調 (Primary)',
    surface: '底色風格 (Surface)',
    darkMode: '深淺模式',
    light: '亮色',
    dark: '深色',
    colors: {
      zinc: 'Zinc',
      blue: '藍色',
      violet: '紫色',
      rose: '玫瑰',
      orange: '橘色',
      green: '綠色',
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
    title: '全端開發範本',
    subtitle: 'Vue 3 + TypeScript + FastAPI + SQLAlchemy',
    modules: '功能模組',
    moduleCards: {
      api: {
        title: 'API 文件',
        desc: 'FastAPI 自動生成的 OpenAPI 文件',
      },
    },
  },

  sidebar: {
    appSubtitle: '企業管理平台',
    copyright: '© 2026 Fullstack Template',
  },

  command: {
    title: '全域搜尋',
    description: '搜尋此應用程式中的頁面與指令。',
    placeholder: '搜尋頁面、指令 (Ctrl+K)…',
    empty: '找不到符合的結果。',
    select: '選擇',
    go: '前往',
    close: '關閉',
  },

  common: {
    loading: '載入中…',
    profile: '個人資料',
    settings: '設定',
    logout: '登出',
  },
  toast: {
    refreshing: '正在重新整理…',
    deleteSuccess: '已刪除',
    cancelSuccess: '已取消',
    createSuccess: '建立成功',
    updateSuccess: '更新成功',
    error: '操作失敗',
    saveSuccess: '儲存成功',
  },
}

export default zhTW
