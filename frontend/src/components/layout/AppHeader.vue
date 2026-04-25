<script setup lang="ts">
  import { Search } from 'lucide-vue-next'
  import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
  import { SidebarTrigger } from '@/components/ui/sidebar'
  import { Button } from '@/components/ui/button'
  import { Separator } from '@/components/ui/separator'
  import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
  } from '@/components/ui/breadcrumb'
  import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
  } from '@/components/ui/tooltip'

  // Layout Components

  import LanguageSwitcher from './LanguageSwitcher.vue'
  import ThemeSwitcher from './ThemeSwitcher.vue'
  import UserMenu from './UserMenu.vue'

  const { breadcrumbs } = useBreadcrumbs()

  const openCommandPalette = () => {
    window.dispatchEvent(new Event('app:command-open'))
  }
</script>

<template>
  <TooltipProvider :delay-duration="300">
    <header class="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div class="flex h-14 items-center px-4 gap-4">

        <!-- Left: Trigger + Breadcrumb -->
        <div class="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger as-child>
              <SidebarTrigger />
            </TooltipTrigger>
            <TooltipContent side="bottom">{{ $t('header.toggleSidebar') }}</TooltipContent>
          </Tooltip>

          <Separator orientation="vertical" class="h-4 mx-1 hidden md:block" />

          <Breadcrumb class="hidden md:flex">
            <BreadcrumbList>
              <template v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
                <BreadcrumbItem>
                  <BreadcrumbLink v-if="index < breadcrumbs.length - 1" as-child>
                    <RouterLink :to="crumb.path">{{ crumb.name }}</RouterLink>
                  </BreadcrumbLink>
                  <BreadcrumbPage v-else>{{ crumb.name }}</BreadcrumbPage>
                </BreadcrumbItem>
                <BreadcrumbSeparator v-if="index < breadcrumbs.length - 1" />
              </template>
            </BreadcrumbList>
          </Breadcrumb>
        </div>

        <!-- Right: Actions -->
        <div class="ml-auto flex items-center gap-2">

          <!-- Search -->
          <Tooltip>
            <TooltipTrigger as-child>
              <Button
                variant="search"
                size="sm"
                class="hidden w-64 md:flex"
                aria-label="Open command palette"
                @click="openCommandPalette"
              >
                <Search class="shrink-0" />
                <span>{{ $t('header.searchPlaceholder') }}</span>
                <kbd class="pointer-events-none absolute right-1.5 top-1.5 hidden h-6 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium sm:flex">
                  <span class="text-xs">⌘</span>K
                </kbd>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">{{ $t('header.searchTooltip') }}</TooltipContent>
          </Tooltip>

          <div class="flex items-center gap-1">

            <LanguageSwitcher />
            <ThemeSwitcher />
            <Separator orientation="vertical" class="h-4 mx-1" />
            <UserMenu />
          </div>
        </div>

      </div>
    </header>
  </TooltipProvider>
</template>
