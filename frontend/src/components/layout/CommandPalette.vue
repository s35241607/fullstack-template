<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMagicKeys } from '@vueuse/core'
import {
  Home,
  Package,
  ShoppingCart,
  Workflow,
  Info,
} from 'lucide-vue-next'

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'

const router = useRouter()
const isOpen = ref(false)

// ── Expose open method for AppHeader ─────────────────────────────────
defineExpose({
  open() {
    isOpen.value = true
  },
})

// ── Global Ctrl+K Shortcut ──────────────────────────────────────────
const { ctrl_k, meta_k } = useMagicKeys()

watch([ctrl_k, meta_k], ([c, m]) => {
  if (c || m) {
    isOpen.value = !isOpen.value
  }
})

// ── All navigable pages ─────────────────────────────────────────────
interface NavItem {
  id: string
  label: string
  description: string
  icon: unknown
  route: string
  group: string
}

const pages: NavItem[] = [
  {
    id: 'home',
    label: 'Dashboard',
    description: '首頁總覽',
    icon: Home,
    route: '/',
    group: '頁面',
  },
  {
    id: 'items',
    label: 'Items',
    description: '管理品項清單',
    icon: Package,
    route: '/items',
    group: '頁面',
  },
  {
    id: 'orders',
    label: '訂單管理',
    description: '管理採購訂單',
    icon: ShoppingCart,
    route: '/orders',
    group: '頁面',
  },
  {
    id: 'hold-summary',
    label: 'On-Hold 總覽',
    description: '查看 On-Hold 訂單彙整',
    icon: ShoppingCart,
    route: '/orders/holds',
    group: '頁面',
  },
  {
    id: 'procurement-plans',
    label: '採購計畫',
    description: '管理與送審採購計畫',
    icon: Package,
    route: '/procurement/plans',
    group: '頁面',
  },
  {
    id: 'bpmn-definitions',
    label: 'Processes',
    description: '流程定義管理',
    icon: Workflow,
    route: '/bpmn/definitions',
    group: '頁面',
  },
  {
    id: 'bpmn-instances',
    label: 'Process Instances',
    description: '流程執行中實例',
    icon: Workflow,
    route: '/bpmn/instances',
    group: '頁面',
  },
  {
    id: 'bpmn-tasks',
    label: 'My Tasks',
    description: '我的待辦任務',
    icon: Workflow,
    route: '/bpmn/tasks',
    group: '頁面',
  },
  {
    id: 'about',
    label: 'About',
    description: '關於此系統',
    icon: Info,
    route: '/about',
    group: '頁面',
  },
]

// Group the items
const groupedPages = pages.reduce((acc, page) => {
  if (!acc[page.group]) {
    acc[page.group] = []
  }
  acc[page.group].push(page)
  return acc
}, {} as Record<string, NavItem[]>)

const handleSelect = (item: NavItem) => {
  isOpen.value = false
  router.push(item.route)
}
</script>

<template>
  <CommandDialog v-model:open="isOpen">
    <CommandInput placeholder="搜尋頁面、指令 (支援 Ctrl+K)..." />
    <CommandList>
      <CommandEmpty>找不到符合的結果。</CommandEmpty>
      <CommandGroup v-for="(items, groupName) in groupedPages" :key="groupName" :heading="groupName">
        <CommandItem
          v-for="item in items"
          :key="item.id"
          :value="item.label"
          @select="() => handleSelect(item)"
        >
          <component :is="item.icon" class="mr-2 h-4 w-4 text-muted-foreground" />
          <div class="flex flex-col">
            <span>{{ item.label }}</span>
            <span class="text-xs text-muted-foreground">{{ item.description }}</span>
          </div>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </CommandDialog>
</template>
