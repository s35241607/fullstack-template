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
    SidebarHeader,
    SidebarRail,
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
    <!-- Header: uses official SidebarMenuButton size="lg" pattern -->
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" tooltip="MyApp">
            <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground text-sm font-bold shadow-sm">
              M
            </div>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold">MyApp</span>
              <span class="truncate text-xs">Enterprise Platform</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <!-- Main -->
      <SidebarGroup>
        <SidebarGroupLabel>Main</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in mainNavItems" :key="item.path">
              <SidebarMenuButton as-child :is-active="route.path === item.path" :tooltip="item.name">
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
              <SidebarMenuButton as-child :is-active="route.path === item.path" :tooltip="item.name">
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
              <SidebarMenuButton as-child :is-active="route.path === item.path" :tooltip="item.name">
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
              <SidebarMenuButton as-child :is-active="route.path === item.path" :tooltip="item.name">
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
              <SidebarMenuButton as-child :is-active="route.path === '/about'" tooltip="About">
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

    <!-- Footer: uses official SidebarMenuButton pattern -->
    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" tooltip="John Doe">
            <div class="flex aspect-square size-8 items-center justify-center rounded-full bg-sidebar-primary text-sidebar-primary-foreground text-xs font-semibold">
              JD
            </div>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold text-xs">John Doe</span>
              <span class="truncate text-[10px] text-muted-foreground">john@example.com</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <!-- Rail: allows hover-to-expand when collapsed -->
    <SidebarRail />
  </Sidebar>
</template>
