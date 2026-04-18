import type { MessageSchema } from './en'

const zhTW: MessageSchema = {
  lang: '中文',

  nav: {
    groups: {
      main: '主要',
      workflow: '工作流程',
      procurement: '採購管理',
      orders: '訂單管理',
      system: '系統',
    },
    items: {
      home: '儀表板',
      items: '品項管理',
      bpmnDefinitions: '流程定義',
      bpmnDefinitionDetail: '流程詳情',
      bpmnInstances: '執行實例',
      bpmnTasks: '我的任務',
      procurementPlans: '採購計畫',
      procurementPlanDetail: '計畫詳情',
      orders: '訂單列表',
      orderDetail: '訂單詳情',
      holdSummary: 'On-Hold 總覽',
      about: '關於',
    },
    desc: {
      home: '首頁總覽',
      items: '管理品項清單',
      bpmnDefinitions: '流程定義管理',
      bpmnInstances: '流程執行中實例',
      bpmnTasks: '我的待辦任務',
      procurementPlans: '管理與送審採購計畫',
      orders: '管理採購訂單',
      holdSummary: '查看 On-Hold 訂單彙整',
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
    title: '企業採購管理系統',
    subtitle: '訂單追蹤 · On-Hold 管理 · 採購計畫審核',
    stats: {
      orders: '進行中訂單',
      holds: 'Hold 暫扣總量',
      plans: '採購計畫',
    },
    modules: '功能模組',
    moduleCards: {
      orders: {
        title: '訂單管理',
        desc: '查看所有採購訂單、品項明細、收貨紀錄與交期追蹤',
      },
      holds: {
        title: 'On-Hold 總覽',
        desc: '依機型彙總 Hold 數量，快速掌握暫扣狀況',
      },
      procurement: {
        title: '採購計畫',
        desc: '建立與管理採購計畫，支援完整審核流程',
      },
      api: {
        title: 'API 文件',
        desc: 'FastAPI 自動生成的 OpenAPI 文件',
      },
    },
  },

  sidebar: {
    appSubtitle: '企業管理平台',
    copyright: '© 2026 Lan Side Project',
  },

  command: {
    placeholder: '搜尋頁面、指令 (Ctrl+K)…',
    empty: '找不到符合的結果。',
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
