<script setup lang="ts">
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
  import { appNavGroups } from '@/config/navigation'

  const route = useRoute()

  const isItemActive = (path: string) => {
    if (path === '/') return route.path === '/'
    return route.path === path || route.path.startsWith(`${path}/`)
  }
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
      <SidebarGroup v-for="group in appNavGroups" :key="group.id">
        <SidebarGroupLabel>{{ group.label }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in group.items" :key="item.path">
              <SidebarMenuButton as-child :is-active="isItemActive(item.path)" :tooltip="item.name">
                <RouterLink :to="item.path" :title="item.name">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter class="p-4 border-t border-sidebar-border/50">
      <div class="flex flex-col gap-1 text-[10px] text-muted-foreground font-medium leading-none">
        <div class="group-data-[collapsible=icon]:hidden">
          © 2024 MyApp Platform
        </div>
        <div class="group-data-[collapsible=icon]:hidden text-[9px] opacity-60">
          All Rights Reserved
        </div>
        <div class="hidden group-data-[collapsible=icon]:flex items-center justify-center font-bold text-xs">
          ©
        </div>
      </div>
    </SidebarFooter>

    <!-- Rail: allows hover-to-expand when collapsed -->
    <SidebarRail />
  </Sidebar>
</template>
