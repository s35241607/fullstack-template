<script setup lang="ts">
/**
 * CommandPalette — a full-featured command/search dialog
 *
 * Features:
 * - Open with Ctrl+K / ⌘K
 * - Close with Escape
 * - ↑ ↓ arrow key navigation
 * - Enter to navigate / execute
 * - Page navigation shortcuts
 * - Quick search across all pages
 */

import {
  ref,
  computed,
  watch,
  nextTick,
  onMounted,
  onUnmounted,
} from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  Home,
  Package,
  ShoppingCart,
  Workflow,
  Info,
  ChevronRight,
  ArrowUp,
  ArrowDown,
  CornerDownLeft,
} from 'lucide-vue-next'

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const activeIndex = ref(0)
const inputRef = ref<HTMLInputElement | null>(null)

// ── All navigable pages ─────────────────────────────────────────────
interface NavItem {
  id: string
  label: string
  description: string
  icon: unknown
  route: string
  keywords: string[]
  group: string
}

const pages: NavItem[] = [
  {
    id: 'home',
    label: 'Dashboard',
    description: '首頁總覽',
    icon: Home,
    route: '/',
    keywords: ['home', 'dashboard', '首頁', '總覽'],
    group: '頁面',
  },
  {
    id: 'items',
    label: 'Items',
    description: '管理品項清單',
    icon: Package,
    route: '/items',
    keywords: ['items', 'list', '品項', '清單'],
    group: '頁面',
  },
  {
    id: 'orders',
    label: '訂單管理',
    description: '管理採購訂單',
    icon: ShoppingCart,
    route: '/orders',
    keywords: ['orders', 'order', '訂單', '採購訂單'],
    group: '頁面',
  },
  {
    id: 'hold-summary',
    label: 'On-Hold 總覽',
    description: '查看 On-Hold 訂單彙整',
    icon: ShoppingCart,
    route: '/orders/holds',
    keywords: ['hold', 'on-hold', 'holds', '扣留'],
    group: '頁面',
  },
  {
    id: 'procurement-plans',
    label: '採購計畫',
    description: '管理與送審採購計畫',
    icon: Package,
    route: '/procurement/plans',
    keywords: ['procurement', 'plan', '採購', '計畫'],
    group: '頁面',
  },
  {
    id: 'bpmn-definitions',
    label: 'Processes',
    description: '流程定義管理',
    icon: Workflow,
    route: '/bpmn/definitions',
    keywords: ['bpmn', 'process', 'workflow', '流程'],
    group: '頁面',
  },
  {
    id: 'bpmn-instances',
    label: 'Process Instances',
    description: '流程執行中實例',
    icon: Workflow,
    route: '/bpmn/instances',
    keywords: ['bpmn', 'instance', '實例'],
    group: '頁面',
  },
  {
    id: 'bpmn-tasks',
    label: 'My Tasks',
    description: '我的待辦任務',
    icon: Workflow,
    route: '/bpmn/tasks',
    keywords: ['task', 'todo', '任務', '待辦'],
    group: '頁面',
  },
  {
    id: 'about',
    label: 'About',
    description: '關於此系統',
    icon: Info,
    route: '/about',
    keywords: ['about', '關於'],
    group: '頁面',
  },
]

// ── Filtered results ────────────────────────────────────────────────
const filtered = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return pages
  return pages.filter(
    (p) =>
      p.label.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.keywords.some((k) => k.includes(q)),
  )
})

// ── Grouped results ─────────────────────────────────────────────────
const grouped = computed(() => {
  const groups: Record<string, NavItem[]> = {}
  for (const item of filtered.value) {
    if (!groups[item.group]) groups[item.group] = []
    groups[item.group].push(item)
  }
  return groups
})

// Flat list for keyboard navigation
const flatList = computed(() => filtered.value)

watch(query, () => {
  activeIndex.value = 0
})

watch(isOpen, async (v) => {
  if (v) {
    query.value = ''
    activeIndex.value = 0
    await nextTick()
    inputRef.value?.focus()
  }
})

// ── Keyboard: open hotkey ────────────────────────────────────────────
function onGlobalKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value = !isOpen.value
  }
}

onMounted(() => window.addEventListener('keydown', onGlobalKeydown))
onUnmounted(() => window.removeEventListener('keydown', onGlobalKeydown))

// ── Keyboard: within dialog ──────────────────────────────────────────
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    isOpen.value = false
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, flatList.value.length - 1)
    scrollActiveIntoView()
    return
  }
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
    scrollActiveIntoView()
    return
  }
  if (e.key === 'Enter') {
    e.preventDefault()
    const item = flatList.value[activeIndex.value]
    if (item) navigate(item)
  }
}

function scrollActiveIntoView() {
  nextTick(() => {
    const el = document.querySelector('[data-active="true"]') as HTMLElement | null
    el?.scrollIntoView({ block: 'nearest' })
  })
}

function navigate(item: NavItem) {
  router.push(item.route)
  isOpen.value = false
}

function getItemIndex(item: NavItem) {
  return flatList.value.indexOf(item)
}
</script>

<template>
  <!-- Trigger (accessible from elsewhere via keyboard shortcut) -->
  <slot :open="() => (isOpen = true)" />

  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="cmd-fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4"
        @mousedown.self="isOpen = false"
      >
        <!-- Backdrop blur -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="isOpen = false" />

        <!-- Dialog -->
        <div
          class="relative z-10 w-full max-w-xl bg-popover border border-border rounded-xl shadow-2xl overflow-hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Command palette"
          @keydown="onKeydown"
        >
          <!-- Search input -->
          <div class="flex items-center gap-3 px-4 py-3 border-b border-border">
            <Search :size="16" class="text-muted-foreground shrink-0" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Search pages…"
              class="flex-1 bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground"
            />
            <kbd
              class="hidden sm:flex items-center text-[10px] bg-muted px-1.5 py-0.5 rounded border border-border/60 font-mono text-muted-foreground gap-0.5"
            >
              ESC
            </kbd>
          </div>

          <!-- Results -->
          <div class="max-h-[340px] overflow-y-auto py-2">
            <!-- No results -->
            <div
              v-if="flatList.length === 0"
              class="px-4 py-8 text-center text-sm text-muted-foreground"
            >
              No results for "{{ query }}"
            </div>

            <!-- Grouped results -->
            <template v-for="(items, group) in grouped" :key="group">
              <div class="px-3 py-1.5">
                <span class="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {{ group }}
                </span>
              </div>
              <button
                v-for="item in items"
                :key="item.id"
                :data-active="getItemIndex(item) === activeIndex"
                class="w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors rounded-lg mx-1"
                :class="
                  getItemIndex(item) === activeIndex
                    ? 'bg-accent text-foreground'
                    : 'text-foreground/70 hover:bg-accent/60'
                "
                style="width: calc(100% - 0.5rem)"
                @mouseenter="activeIndex = getItemIndex(item)"
                @click="navigate(item)"
              >
                <span
                  class="flex items-center justify-center size-7 rounded-md bg-muted shrink-0"
                >
                  <component :is="item.icon" :size="14" />
                </span>
                <span class="flex-1 min-w-0">
                  <span class="block text-sm font-medium leading-tight">{{ item.label }}</span>
                  <span class="block text-xs text-muted-foreground leading-tight mt-0.5">{{
                    item.description
                  }}</span>
                </span>
                <ChevronRight :size="14" class="text-muted-foreground/40 shrink-0" />
              </button>
            </template>
          </div>

          <!-- Footer hints -->
          <div
            class="flex items-center gap-4 px-4 py-2.5 border-t border-border bg-muted/40 text-[11px] text-muted-foreground"
          >
            <span class="flex items-center gap-1">
              <ArrowUp :size="11" />
              <ArrowDown :size="11" />
              Navigate
            </span>
            <span class="flex items-center gap-1">
              <CornerDownLeft :size="11" />
              Open
            </span>
            <span class="flex items-center gap-1">
              <kbd class="font-mono">ESC</kbd>
              Close
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.cmd-fade-enter-active,
.cmd-fade-leave-active {
  transition: opacity 0.15s ease;
}
.cmd-fade-enter-from,
.cmd-fade-leave-to {
  opacity: 0;
}

.cmd-fade-enter-active .relative,
.cmd-fade-leave-active .relative {
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.cmd-fade-enter-from .relative,
.cmd-fade-leave-to .relative {
  transform: scale(0.96) translateY(-8px);
  opacity: 0;
}
</style>
