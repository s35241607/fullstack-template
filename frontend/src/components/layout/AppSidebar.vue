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
  import { Heart } from 'lucide-vue-next'
  import { useRoute } from 'vue-router'
  import { useI18n } from 'vue-i18n'
  import { appNavGroups } from '@/config/navigation'

  const route = useRoute()
  const { t } = useI18n()

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
          <SidebarMenuButton size="lg" tooltip="MyApp" class="cursor-pointer" as-child>
            <RouterLink to="/">
              <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground text-sm font-bold shadow-sm">
                M
              </div>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">MyApp</span>
                <span class="truncate text-xs">{{ $t('sidebar.appSubtitle') }}</span>
              </div>
            </RouterLink>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup v-for="group in appNavGroups" :key="group.id">
        <SidebarGroupLabel>{{ t(group.label) }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in group.items" :key="item.path">
              <SidebarMenuButton
                as-child
                :is-active="isItemActive(item.path)"
                :tooltip="t(item.name)"
              >
                <RouterLink :to="item.path" :title="t(item.name)">
                  <component :is="item.icon" />
                  <span class="font-medium tracking-wide">{{ t(item.name) }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <!-- Footer: Responsive Copyright Notice -->
    <SidebarFooter class="p-4 border-t border-sidebar-border/50">
      <!-- Full Copyright (Visible when expanded) -->
      <div class="group-data-[collapsible=icon]:hidden flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground font-medium leading-tight">
        <span>{{ $t('sidebar.copyright') }}</span>
        <Heart :size="10" class="text-rose-500 fill-rose-500" />
      </div>

      <!-- Minimalist Copyright (Visible when collapsed) -->
      <div class="hidden group-data-[collapsible=icon]:flex items-center justify-center font-bold text-xs text-muted-foreground">
        ©
      </div>
    </SidebarFooter>

    <!-- Rail: allows hover-to-expand when collapsed -->
    <SidebarRail />
  </Sidebar>
</template>
