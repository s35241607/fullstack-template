<script setup lang="ts">
  import { Palette, Check, Sun, Moon } from 'lucide-vue-next'
  import { useTheme } from '@/composables/useTheme'
  import { Button } from '@/components/ui/button'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    Tooltip,
    TooltipContent,
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
</script>

<template>
  <Tooltip>
    <TooltipTrigger as-child>
      <div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon-sm" aria-label="Open theme settings">
              <Palette />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent :side-offset="8" align="end" class="w-64 p-0 border-border shadow-lg overflow-hidden">
            <DropdownMenuLabel class="px-4 py-3 flex flex-col gap-1 bg-muted/30 border-b border-border">
              <span class="text-sm font-semibold leading-none">{{ $t('theme.title') }}</span>
              <span class="text-[11px] text-muted-foreground font-normal">{{ $t('theme.subtitle') }}</span>
            </DropdownMenuLabel>
            
            <div class="p-3 space-y-4">
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
</template>
