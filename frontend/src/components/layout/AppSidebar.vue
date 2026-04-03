<script setup lang="ts">
  import {
    Info,
    Package,
    ChevronLeft,
    ChevronRight,
    LayoutDashboard,
    GitFork,
    ListTodo,
    Workflow,
    ShoppingCart,
    ClipboardList,
    PauseCircle,
  } from 'lucide-vue-next'

  defineProps<{
    collapsed: boolean
  }>()

  defineEmits<{
    toggle: []
  }>()

  const mainNavItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard, exact: true },
    { name: 'Items', path: '/items', icon: Package },
  ]

  const bpmnNavItems = [
    { name: 'Processes', path: '/bpmn/definitions', icon: Workflow },
    { name: 'Instances', path: '/bpmn/instances', icon: GitFork },
    { name: 'My Tasks', path: '/bpmn/tasks', icon: ListTodo },
  ]

  const procurementNavItems = [{ name: '採購計畫', path: '/procurement/plans', icon: ShoppingCart }]

  const orderNavItems = [
    { name: '訂單列表', path: '/orders', icon: ClipboardList },
    { name: 'On-Hold 總覽', path: '/orders/holds', icon: PauseCircle },
  ]
</script>

<template>
  <!-- Wrapper: overflow visible so toggle button isn't clipped -->
  <div
    class="relative flex flex-col h-full bg-sidebar border-r border-border transition-[width] duration-300 ease-in-out shadow-sm"
    :class="collapsed ? 'w-16' : 'w-64'"
  >
    <!-- Brand -->
    <div class="flex items-center h-14 px-4 border-b border-border shrink-0 overflow-hidden">
      <div class="flex items-center gap-2.5 min-w-0">
        <div
          class="flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground shrink-0 text-sm font-bold shadow-sm"
        >
          M
        </div>
        <div
          class="overflow-hidden transition-all duration-200"
          :class="collapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'"
        >
          <span class="font-semibold text-foreground whitespace-nowrap text-sm tracking-tight"
            >MyApp</span
          >
          <p class="text-[10px] text-muted-foreground whitespace-nowrap leading-tight">
            Enterprise Platform
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-3 overflow-y-auto overflow-x-hidden">
      <!-- Main -->
      <div class="px-3 mb-1">
        <div
          v-if="!collapsed"
          class="px-1 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
        >
          Main
        </div>
        <div class="space-y-0.5">
          <RouterLink
            v-for="item in mainNavItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors group"
            active-class="!bg-accent !text-foreground font-medium"
            :exact-active-class="item.exact ? '!bg-accent !text-foreground font-medium' : undefined"
            :title="collapsed ? item.name : undefined"
          >
            <component :is="item.icon" class="shrink-0" :size="17" />
            <span
              class="whitespace-nowrap transition-all duration-200 overflow-hidden"
              :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
            >
              {{ item.name }}
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- Divider -->
      <div class="mx-3 my-2 border-t border-border/60" />

      <!-- BPMN -->
      <div class="px-3">
        <div
          v-if="!collapsed"
          class="px-1 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
        >
          Workflow
        </div>
        <div class="space-y-0.5">
          <RouterLink
            v-for="item in bpmnNavItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors group"
            active-class="!bg-accent !text-foreground font-medium"
            :title="collapsed ? item.name : undefined"
          >
            <component :is="item.icon" class="shrink-0" :size="17" />
            <span
              class="whitespace-nowrap transition-all duration-200 overflow-hidden"
              :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
            >
              {{ item.name }}
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- Divider -->
      <div class="mx-3 my-2 border-t border-border/60" />

      <!-- Procurement -->
      <div class="px-3">
        <div
          v-if="!collapsed"
          class="px-1 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
        >
          採購管理
        </div>
        <div class="space-y-0.5">
          <RouterLink
            v-for="item in procurementNavItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors group"
            active-class="!bg-accent !text-foreground font-medium"
            :title="collapsed ? item.name : undefined"
          >
            <component :is="item.icon" class="shrink-0" :size="17" />
            <span
              class="whitespace-nowrap transition-all duration-200 overflow-hidden"
              :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
            >
              {{ item.name }}
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- Divider -->
      <div class="mx-3 my-2 border-t border-border/60" />

      <!-- Orders -->
      <div class="px-3">
        <div
          v-if="!collapsed"
          class="px-1 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
        >
          訂單管理
        </div>
        <div class="space-y-0.5">
          <RouterLink
            v-for="item in orderNavItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors group"
            active-class="!bg-accent !text-foreground font-medium"
            :title="collapsed ? item.name : undefined"
          >
            <component :is="item.icon" class="shrink-0" :size="17" />
            <span
              class="whitespace-nowrap transition-all duration-200 overflow-hidden"
              :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
            >
              {{ item.name }}
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- Divider -->
      <div class="mx-3 my-2 border-t border-border/60" />

      <!-- System -->
      <div class="px-3">
        <div
          v-if="!collapsed"
          class="px-1 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60"
        >
          System
        </div>
        <RouterLink
          to="/about"
          class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          active-class="!bg-accent !text-foreground font-medium"
          :title="collapsed ? 'About' : undefined"
        >
          <Info class="shrink-0" :size="17" />
          <span
            class="whitespace-nowrap transition-all duration-200 overflow-hidden"
            :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
          >
            About
          </span>
        </RouterLink>
      </div>
    </nav>

    <!-- Footer user -->
    <div class="border-t border-border px-3 py-3 shrink-0">
      <div
        class="flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:bg-accent transition-colors cursor-pointer overflow-hidden"
      >
        <div
          class="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs font-semibold shrink-0"
        >
          JD
        </div>
        <div
          class="overflow-hidden transition-all duration-200 min-w-0"
          :class="collapsed ? 'opacity-0 w-0' : 'opacity-100'"
        >
          <p class="text-xs font-medium text-foreground whitespace-nowrap">John Doe</p>
          <p class="text-[10px] text-muted-foreground whitespace-nowrap">john@example.com</p>
        </div>
      </div>
    </div>

    <!-- Collapse toggle — absolutely positioned to hang off the right edge -->
    <button
      class="absolute -right-3 top-[3.75rem] z-20 flex items-center justify-center w-6 h-6 rounded-full bg-sidebar border border-border shadow-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      @click="$emit('toggle')"
    >
      <ChevronLeft v-if="!collapsed" :size="12" />
      <ChevronRight v-else :size="12" />
    </button>
  </div>
</template>
