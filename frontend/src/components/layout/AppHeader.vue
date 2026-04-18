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
    Globe,
  } from 'lucide-vue-next'
  import { useTheme } from '@/composables/useTheme'
  import { useLocale, supportedLocales } from '@/composables/useLocale'
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
  const { locale, setLocale } = useLocale()
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
                class="relative hidden h-9 w-64 items-center justify-start rounded-md border border-input bg-muted/50 px-3 text-sm text-muted-foreground hover:bg-accent hover:text-foreground md:flex group cursor-pointer"
              >
                <Search class="mr-2 h-4 w-4" />
                <span>{{ $t('header.searchPlaceholder') }}</span>
                <kbd class="pointer-events-none absolute right-1.5 top-1.5 hidden h-6 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium sm:flex">
                  <span class="text-xs">⌘</span>K
                </kbd>
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom">{{ $t('header.searchTooltip') }}</TooltipContent>
          </Tooltip>

          <div class="flex items-center gap-1">
            <!-- Notifications -->
            <Tooltip>
              <TooltipTrigger as-child>
                <div class="flex">
                  <NotificationPanel />
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">{{ $t('header.notificationsTooltip') }}</TooltipContent>
            </Tooltip>

            <!-- Language Switcher -->
            <Tooltip>
              <TooltipTrigger as-child>
                <div>
                  <DropdownMenu>
                    <DropdownMenuTrigger as-child>
                      <Button variant="ghost" size="icon-sm" aria-label="Switch language">
                        <Globe class="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" class="w-40">
                      <DropdownMenuLabel class="text-xs text-muted-foreground font-normal">
                        {{ $t('header.langTooltip') }}
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        v-for="loc in supportedLocales"
                        :key="loc.value"
                        class="cursor-pointer gap-2"
                        @click="setLocale(loc.value)"
                      >
                        <Check class="h-3.5 w-3.5" :class="locale === loc.value ? 'opacity-100' : 'opacity-0'" />
                        <span>{{ loc.label }}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">{{ $t('header.langTooltip') }}</TooltipContent>
            </Tooltip>

            <!-- Theme: Wrapped with div to avoid event conflicts -->
            <Tooltip>
              <TooltipTrigger as-child>
                <div>
                  <DropdownMenu>
                    <DropdownMenuTrigger as-child>
                      <Button variant="ghost" size="icon-sm" aria-label="Open theme settings">
                        <Palette class="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" class="w-64 p-3 border-border shadow-lg">
                      <div class="space-y-4">
                        <div>
                          <h4 class="text-sm font-semibold leading-none mb-1">{{ $t('theme.title') }}</h4>
                          <p class="text-[11px] text-muted-foreground">{{ $t('theme.subtitle') }}</p>
                        </div>

                        <!-- Primary Colors -->
                        <div class="space-y-2">
                          <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">{{ $t('theme.primaryColor') }}</p>
                          <div class="grid grid-cols-3 gap-2">
                            <button
                              v-for="theme in themes"
                              :key="theme.id"
                              class="flex flex-col items-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent cursor-pointer"
                              :class="{ 'border-primary/20 bg-accent/50': currentTheme === theme.id }"
                              @click="setTheme(theme.id)"
                            >
                              <span
                                class="flex h-6 w-6 items-center justify-center rounded-full border-2 shadow-sm"
                                :style="{ backgroundColor: theme.color, borderColor: currentTheme === theme.id ? 'white' : 'transparent' }"
                              >
                                <Check v-if="currentTheme === theme.id" :size="12" class="text-white" />
                              </span>
                              <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">{{ $t(`theme.colors.${theme.id}`) }}</span>
                            </button>
                          </div>
                        </div>

                        <!-- Surface Styles -->
                        <div class="space-y-2">
                          <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">{{ $t('theme.surface') }}</p>
                          <div class="grid grid-cols-3 gap-2">
                            <button
                              v-for="surface in surfaces"
                              :key="surface.id"
                              class="flex flex-col items-center gap-1.5 p-2 rounded-lg hover:bg-accent transition-colors group relative border border-transparent cursor-pointer"
                              :class="{ 'border-primary/20 bg-accent/50': currentSurface === surface.id }"
                              @click="setSurface(surface.id)"
                            >
                              <span
                                class="flex h-6 w-6 items-center justify-center rounded-full border-2 shadow-sm"
                                :style="{ backgroundColor: surface.color, borderColor: currentSurface === surface.id ? 'white' : 'transparent' }"
                              >
                                <Check v-if="currentSurface === surface.id" :size="12" class="text-white" />
                              </span>
                              <span class="text-[10px] font-medium text-muted-foreground group-hover:text-foreground">{{ $t(`theme.surfaces.${surface.id}`) }}</span>
                            </button>
                          </div>
                        </div>

                        <!-- Dark Mode Toggle -->
                        <div class="pt-2 border-t border-border">
                          <h4 class="text-sm font-semibold leading-none mb-2">{{ $t('theme.darkMode') }}</h4>
                          <div class="flex p-1 bg-muted rounded-lg border border-border/50">
                            <button
                              class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer"
                              :class="!isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                              @click="isDark && toggleDark()"
                            >
                              <Sun :size="14" /> {{ $t('theme.light') }}
                            </button>
                            <button
                              class="flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer"
                              :class="isDark ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                              @click="!isDark && toggleDark()"
                            >
                              <Moon :size="14" /> {{ $t('theme.dark') }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">{{ $t('header.themeTooltip') }}</TooltipContent>
            </Tooltip>

            <div class="h-4 w-[1px] bg-border mx-1" />

            <!-- User: Wrapped with div to avoid event conflicts -->
            <Tooltip>
              <TooltipTrigger as-child>
                <div>
                  <DropdownMenu>
                    <DropdownMenuTrigger as-child>
                      <button
                        aria-label="Open user menu"
                        class="flex h-9 w-9 items-center justify-center rounded-full border-2 border-transparent overflow-hidden hover:border-accent shadow-sm hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer"
                      >
                        <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" class="h-full w-full object-cover" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" class="border-border shadow-lg">
                      <DropdownMenuLabel>{{ $t('header.myAccount') }}</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem class="cursor-pointer">
                        <User class="mr-2 h-4 w-4" />
                        <span>{{ $t('common.profile') }}</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem class="cursor-pointer">
                        <Settings class="mr-2 h-4 w-4" />
                        <span>{{ $t('common.settings') }}</span>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem class="text-destructive focus:bg-destructive focus:text-destructive-foreground cursor-pointer">
                        <LogOut class="mr-2 h-4 w-4" />
                        <span>{{ $t('common.logout') }}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">{{ $t('header.accountTooltip') }}</TooltipContent>
            </Tooltip>
          </div>
        </div>

      </div>
    </header>
  </TooltipProvider>
</template>
