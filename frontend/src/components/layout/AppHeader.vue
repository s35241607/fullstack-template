<script setup lang="ts">
  import {
    Search,
    Sun,
    Moon,
    Check,
    User,
    LogOut,
    Settings,
    Palette,
  } from 'lucide-vue-next'
  import { useTheme } from '@/composables/useTheme'
  import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
  import NotificationPanel from './NotificationPanel.vue'
  import { SidebarTrigger } from '@/components/ui/sidebar'
  import { Button } from '@/components/ui/button'
  import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
  } from '@/components/ui/breadcrumb'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
  } from '@/components/ui/tooltip'

  const {
    isDark,
    toggleDark,
    themes,
    currentTheme,
    setTheme,
    surfaces,
    currentSurface,
    setSurface,
  } = useTheme()
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
            <TooltipContent side="bottom">收起/展開側邊欄</TooltipContent>
          </Tooltip>

          <div class="h-4 w-[1px] bg-border mx-1 hidden md:block" />

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
              <button
                @click="openCommandPalette"
                aria-label="Open command palette"
                class="relative hidden h-9 w-64 items-center justify-start rounded-md border border-input bg-muted/50 px-3 text-sm text-muted-foreground hover:bg-accent hover:text-foreground md:flex group"
              >
                <Search class="mr-2 h-4 w-4" />
                <span>Search…</span>
                <kbd class="pointer-events-none absolute right-1.5 top-1.5 hidden h-6 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium sm:flex">
                  <span class="text-xs">⌘</span>K
                </kbd>
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom">搜尋頁面 (Ctrl+K)</TooltipContent>
          </Tooltip>

          <div class="flex items-center gap-1">
            <!-- Notifications -->
            <Tooltip>
              <TooltipTrigger as-child>
                <div class="flex">
                  <NotificationPanel />
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">通知中心</TooltipContent>
            </Tooltip>

            <!-- Theme -->
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger as-child>
                  <DropdownMenuTrigger as-child>
                    <Button variant="ghost" size="icon-sm" aria-label="Open theme settings">
                      <Palette class="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="bottom">配色方案與外觀切換</TooltipContent>
              </Tooltip>
              <DropdownMenuContent align="end" class="w-64 p-3">
                <div class="space-y-4">
                  <div>
                    <h4 class="text-sm font-semibold leading-none mb-1">個性化設定</h4>
                    <p class="text-[11px] text-muted-foreground">自定義您的應用程式視覺風格</p>
                  </div>

                  <!-- Primary Colors -->
                  <div class="space-y-2">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">主色調 (Primary)</p>
                    <div class="grid grid-cols-3 gap-2">
                      <button
                        v-for="theme in themes"
                        :key="theme.id"
                        class="flex flex-col items-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent"
                        :class="{ 'border-primary/20 bg-accent/50': currentTheme === theme.id }"
                        @click="setTheme(theme.id)"
                      >
                        <span
                          class="flex h-6 w-6 items-center justify-center rounded-full border-2 shadow-sm"
                          :style="{ backgroundColor: theme.color, borderColor: currentTheme === theme.id ? 'white' : 'transparent' }"
                        >
                          <Check v-if="currentTheme === theme.id" :size="12" class="text-white" />
                        </span>
                        <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">{{ theme.label }}</span>
                      </button>
                    </div>
                  </div>

                  <!-- Surface Styles -->
                  <div class="space-y-2">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">底色風格 (Surface)</p>
                    <div class="grid grid-cols-3 gap-2">
                      <button
                        v-for="surface in surfaces"
                        :key="surface.id"
                        class="flex flex-col items-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent"
                        :class="{ 'border-primary/20 bg-accent/50': currentSurface === surface.id }"
                        @click="setSurface(surface.id)"
                      >
                        <span
                          class="flex h-6 w-6 items-center justify-center rounded-full border-2 shadow-sm"
                          :style="{ backgroundColor: surface.color, borderColor: currentSurface === surface.id ? 'white' : 'transparent' }"
                        >
                          <Check v-if="currentSurface === surface.id" :size="12" class="text-white" />
                        </span>
                        <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">{{ surface.label }}</span>
                      </button>
                    </div>
                  </div>

                  <!-- Dark / Light mode -->
                  <div class="pt-2 border-t border-border">
                    <h4 class="text-sm font-semibold leading-none mb-2">深淺模式</h4>
                    <div class="flex p-1 bg-muted rounded-lg border border-border/50">
                      <button
                        class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors"
                        :class="!isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                        @click="isDark && toggleDark()"
                      >
                        <Sun :size="14" /> 亮色
                      </button>
                      <button
                        class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors"
                        :class="isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                        @click="!isDark && toggleDark()"
                      >
                        <Moon :size="14" /> 深色
                      </button>
                    </div>
                  </div>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>

            <div class="h-4 w-[1px] bg-border mx-1" />

            <!-- User -->
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger as-child>
                  <DropdownMenuTrigger as-child>
                    <button
                      aria-label="Open user menu"
                      class="flex h-9 w-9 items-center justify-center rounded-full border-2 border-transparent overflow-hidden hover:border-accent shadow-sm hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" class="h-full w-full object-cover" />
                    </button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="bottom">我的帳號</TooltipContent>
              </Tooltip>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User class="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings class="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem class="text-destructive focus:bg-destructive focus:text-destructive-foreground">
                  <LogOut class="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

      </div>
    </header>
  </TooltipProvider>
</template>
