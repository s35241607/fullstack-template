<script setup lang="ts">
  import {
    Info,
    Package,
    LayoutDashboard,
    GitFork,
    ListTodo,
    Workflow,
    ShoppingCart,
    ClipboardList,
    PauseCircle,
  } from 'lucide-vue-next'

  import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarFooter,
    SidebarHeader
  } from '@/components/ui/sidebar'
  import { useRoute } from 'vue-router'

  const route = useRoute()

  const mainNavItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
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
  <Sidebar collapsible="icon">
    <!-- Header -->
    <SidebarHeader>
      <div class="flex items-center gap-2 px-2 py-2">
        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground text-sm font-bold shadow-sm">
          M
        </div>
        <div class="flex flex-col group-data-[collapsible=icon]:hidden">
          <span class="font-semibold text-foreground whitespace-nowrap text-sm tracking-tight">MyApp</span>
          <p class="text-[10px] text-muted-foreground whitespace-nowrap leading-tight">Enterprise Platform</p>
        </div>
      </div>
    </SidebarHeader>

    <SidebarContent>
      <!-- Main -->
      <SidebarGroup>
        <SidebarGroupLabel>Main</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in mainNavItems" :key="item.path">
              <SidebarMenuButton as-child :is-active="route.path === item.path">
                <RouterLink :to="item.path" :title="item.name">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Workflow -->
      <SidebarGroup>
        <SidebarGroupLabel>Workflow</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in bpmnNavItems" :key="item.path">
              <SidebarMenuButton as-child :is-active="route.path === item.path">
                <RouterLink :to="item.path" :title="item.name">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Procurement -->
      <SidebarGroup>
        <SidebarGroupLabel>採購管理</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in procurementNavItems" :key="item.path">
              <SidebarMenuButton as-child :is-active="route.path === item.path">
                <RouterLink :to="item.path" :title="item.name">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Orders -->
      <SidebarGroup>
        <SidebarGroupLabel>訂單管理</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in orderNavItems" :key="item.path">
              <SidebarMenuButton as-child :is-active="route.path === item.path">
                <RouterLink :to="item.path" :title="item.name">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- System -->
      <SidebarGroup>
        <SidebarGroupLabel>System</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton as-child :is-active="route.path === '/about'">
                <RouterLink to="/about" title="About">
                  <Info />
                  <span>About</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <div class="flex items-center gap-2.5 px-2 py-2 rounded-md hover:bg-accent transition-colors overflow-hidden group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:justify-center">
        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-xs font-semibold shrink-0">
          JD
        </div>
        <div class="flex flex-col min-w-0 group-data-[collapsible=icon]:hidden">
          <p class="text-xs font-medium text-foreground whitespace-nowrap">John Doe</p>
          <p class="text-[10px] text-muted-foreground whitespace-nowrap">john@example.com</p>
        </div>
      </div>
    </SidebarFooter>
  </Sidebar>
</template>
