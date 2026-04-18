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
  <header
    class="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
  >
    <div class="flex h-14 items-center px-4 gap-4">
      <div class="flex items-center gap-2">
        <SidebarTrigger class="h-9 w-9" />
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

      <div class="ml-auto flex items-center gap-2">
        <!-- Search Bar -->
        <button
          @click="openCommandPalette"
          aria-label="Open command palette"
          class="relative hidden h-9 w-64 items-center justify-start rounded-md border border-input bg-muted/50 px-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground md:flex cursor-pointer"
        >
          <Search class="mr-2 h-4 w-4" />
          <span>Search…</span>
          <kbd
            class="pointer-events-none absolute right-1.5 top-1.5 hidden h-6 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex"
          >
            <span class="text-xs">⌘</span>K
          </kbd>
        </button>

        <div class="flex items-center gap-1">
          <!-- Notification -->
          <NotificationPanel />

          <!-- Theme -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <button
                aria-label="Open theme settings"
                class="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
              >
                <Palette class="h-4 w-4" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-64 p-3">
              <div class="space-y-4">
                <div>
                  <h4 class="text-sm font-semibold leading-none mb-1">配色方案</h4>
                  <p class="text-[11px] text-muted-foreground">選擇您的應用程式主色與底色</p>
                </div>

                <!-- Primary Colors -->
                <div class="space-y-2">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">主色調</span>
                  <div class="grid grid-cols-3 gap-2">
                    <button
                      v-for="theme in themes"
                      :key="theme.id"
                      class="flex flex-col items-center justify-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent cursor-pointer"
                      :class="{ 'border-primary/20 bg-accent/50': currentTheme === theme.id }"
                      @click="setTheme(theme.id)"
                    >
                      <span
                        class="flex h-6 w-6 items-center justify-center rounded-full border-2 transition-colors shadow-sm"
                        :style="{ backgroundColor: theme.color, borderColor: currentTheme === theme.id ? 'white' : 'transparent' }"
                      >
                        <Check v-if="currentTheme === theme.id" :size="12" class="text-white drop-shadow-sm" />
                      </span>
                      <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">
                        {{ theme.label }}
                      </span>
                    </button>
                  </div>
                </div>

                <!-- Surface Colors -->
                <div class="space-y-2">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">底色風格</span>
                  <div class="grid grid-cols-3 gap-2">
                    <button
                      v-for="surface in surfaces"
                      :key="surface.id"
                      class="flex flex-col items-center justify-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent cursor-pointer"
                      :class="{ 'border-primary/20 bg-accent/50': currentSurface === surface.id }"
                      @click="setSurface(surface.id)"
                    >
                      <span
                        class="flex h-6 w-6 items-center justify-center rounded-full border-2 transition-colors shadow-sm"
                        :style="{ backgroundColor: surface.color, borderColor: currentSurface === surface.id ? 'white' : 'transparent' }"
                      >
                        <Check v-if="currentSurface === surface.id" :size="12" class="text-white drop-shadow-sm" />
                      </span>
                      <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">
                        {{ surface.label }}
                      </span>
                    </button>
                  </div>
                </div>

                <div class="pt-2 border-t border-border">
                  <h4 class="text-sm font-semibold leading-none mb-2">外觀模式</h4>
                  <div class="flex p-1 bg-muted rounded-lg border border-border/50">
                    <button
                      class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer"
                      :class="!isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                      @click="isDark && toggleDark()"
                    >
                      <Sun :size="14" />
                      亮色
                    </button>
                    <button
                      class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer"
                      :class="isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                      @click="!isDark && toggleDark()"
                    >
                      <Moon :size="14" />
                      深色
                    </button>
                  </div>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          <!-- Divider -->
          <div class="h-4 w-[1px] bg-border mx-1" />

          <!-- User -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <button
                aria-label="Open user menu"
                class="flex h-9 w-9 items-center justify-center rounded-full border-2 border-transparent overflow-hidden transition-all hover:bg-accent hover:border-accent shadow-sm hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
              >
                <img 
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" 
                  alt="Avatar" 
                  class="h-full w-full object-cover"
                />
              </button>
            </DropdownMenuTrigger>
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
</template>
