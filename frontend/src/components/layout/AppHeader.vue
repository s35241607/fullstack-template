<script setup lang="ts">
  import { ref } from 'vue'
  import {
    Sun,
    Moon,
    Home,
    ChevronRight,
    AlignCenter,
    AlignJustify,
    Palette,
    Check,
    Search,
  } from 'lucide-vue-next'
  import { useDark, useToggle, onClickOutside } from '@vueuse/core'
  import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
  import { useTheme } from '@/composables/useTheme'
  import NotificationPanel from '@/components/layout/NotificationPanel.vue'
  import CommandPalette from '@/components/layout/CommandPalette.vue'
  import Tooltip from '@/components/ui/tooltip/Tooltip.vue'
  import { SidebarTrigger } from '@/components/ui/sidebar'

  const isDark = useDark()
  const toggleDark = useToggle(isDark)
  const { breadcrumbs } = useBreadcrumbs()
  const { currentTheme, themes, isNarrow, setTheme, toggleWidth } = useTheme()

  // Theme popover
  const themePopoverOpen = ref(false)
  const themePopoverRef = ref<HTMLElement | null>(null)

  onClickOutside(themePopoverRef, () => {
    themePopoverOpen.value = false
  })

  // Command palette — directly call .open() via ref (defineExpose in CommandPalette)
  const cmdPaletteRef = ref<InstanceType<typeof CommandPalette> | null>(null)

  function openCommandPalette() {
    cmdPaletteRef.value?.open()
  }
</script>

<template>
  <!-- Command Palette — always mounted; Ctrl+K also works globally -->
  <CommandPalette ref="cmdPaletteRef" />

  <div class="shrink-0">
    <header class="flex items-center h-14 px-4 gap-3 border-b border-border bg-card shadow-sm z-20 relative">
      <SidebarTrigger class="-ml-2" />

      <!-- Breadcrumbs -->
      <nav
        class="flex items-center gap-1 text-sm flex-1 min-w-0 overflow-hidden"
        aria-label="Breadcrumb"
      >
        <RouterLink
          to="/"
          class="flex items-center text-muted-foreground hover:text-foreground transition-colors shrink-0"
          aria-label="Home"
        >
          <Home :size="15" />
        </RouterLink>

        <template v-for="(crumb, i) in breadcrumbs" :key="crumb.path">
          <ChevronRight :size="13" class="text-muted-foreground/40 shrink-0 mx-0.5" />
          <RouterLink
            v-if="i < breadcrumbs.length - 1"
            :to="crumb.path"
            class="text-muted-foreground hover:text-foreground transition-colors truncate shrink-0"
          >
            {{ crumb.name }}
          </RouterLink>
          <span v-else class="text-foreground font-medium truncate">{{ crumb.name }}</span>
        </template>
      </nav>

      <!-- Right side actions -->
      <div class="flex items-center gap-1 shrink-0">
        <!-- Search / Command palette trigger (md+) -->
        <Tooltip content="搜尋 (Ctrl+K)" side="bottom">
          <button
            class="hidden md:flex items-center gap-2 px-2.5 py-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors text-sm"
            aria-label="Open search"
            @click="openCommandPalette"
          >
            <Search :size="16" />
            <span class="hidden lg:inline text-xs">Search</span>
            <kbd
              class="hidden lg:inline-flex items-center text-[10px] bg-muted px-1.5 py-0.5 rounded border border-border/60 font-mono text-muted-foreground"
            >
              ⌘K
            </kbd>
          </button>
        </Tooltip>

        <!-- Search icon (mobile) -->
        <Tooltip content="搜尋" side="bottom">
          <button
            class="md:hidden p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            aria-label="Open search"
            @click="openCommandPalette"
          >
            <Search :size="18" />
          </button>
        </Tooltip>

        <!-- Notifications -->
        <NotificationPanel />

        <!-- Layout width toggle -->
        <Tooltip :content="isNarrow ? '切換寬版（延伸全寬）' : '切換窄版（靠中對齊）'" side="bottom">
          <button
            class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            :aria-label="isNarrow ? 'Switch to wide layout' : 'Switch to narrow layout'"
            @click="toggleWidth"
          >
            <!-- Narrow mode active: show AlignJustify to switch to wide -->
            <AlignJustify v-if="isNarrow" :size="18" />
            <!-- Wide mode active: show AlignCenter to switch to narrow -->
            <AlignCenter v-else :size="18" />
          </button>
        </Tooltip>

        <!-- Theme color picker -->
        <div class="relative" ref="themePopoverRef">
          <Tooltip content="主題顏色" side="bottom">
            <button
              class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              aria-label="Choose theme color"
              @click="themePopoverOpen = !themePopoverOpen"
            >
              <Palette :size="18" />
            </button>
          </Tooltip>

          <!-- Color palette popover -->
          <Transition name="popover">
            <div
              v-if="themePopoverOpen"
              class="absolute right-0 top-full mt-2 w-44 bg-popover border border-border rounded-xl shadow-xl p-3 z-50"
            >
              <p class="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-2 px-1">
                主題顏色
              </p>
              <div class="grid grid-cols-3 gap-1.5">
                <button
                  v-for="theme in themes"
                  :key="theme.id"
                  class="flex flex-col items-center gap-1 p-1.5 rounded-lg hover:bg-accent transition-colors group"
                  :title="theme.label"
                  @click="setTheme(theme.id); themePopoverOpen = false"
                >
                  <span
                    class="relative flex items-center justify-center size-7 rounded-full border-2 transition-all"
                    :style="{ backgroundColor: theme.color, borderColor: currentTheme === theme.id ? theme.color : 'transparent' }"
                  >
                    <Check
                      v-if="currentTheme === theme.id"
                      :size="13"
                      class="text-white drop-shadow"
                    />
                  </span>
                  <span class="text-[10px] text-muted-foreground group-hover:text-foreground transition-colors">
                    {{ theme.label }}
                  </span>
                </button>
              </div>

              <div class="mt-3 pt-2.5 border-t border-border">
                <p class="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-2 px-1">
                  外觀
                </p>
                <div class="flex gap-1.5">
                  <button
                    class="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg text-xs transition-colors"
                    :class="!isDark ? 'bg-primary text-primary-foreground' : 'hover:bg-accent text-muted-foreground'"
                    @click="isDark && toggleDark()"
                  >
                    <Sun :size="12" />
                    亮色
                  </button>
                  <button
                    class="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg text-xs transition-colors"
                    :class="isDark ? 'bg-primary text-primary-foreground' : 'hover:bg-accent text-muted-foreground'"
                    @click="!isDark && toggleDark()"
                  >
                    <Moon :size="12" />
                    深色
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Dark/light quick toggle -->
        <Tooltip :content="isDark ? '切換亮色模式' : '切換深色模式'" side="bottom">
          <button
            class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            @click="toggleDark()"
          >
            <Sun v-if="isDark" :size="18" />
            <Moon v-else :size="18" />
          </button>
        </Tooltip>

        <!-- Divider -->
        <div class="w-px h-5 bg-border mx-1"></div>

        <!-- User avatar -->
        <Tooltip content="使用者設定" side="bottom">
          <button
            class="flex items-center gap-2 rounded-full hover:opacity-80 transition-opacity"
            aria-label="User profile"
          >
            <div
              class="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs font-semibold"
            >
              JD
            </div>
          </button>
        </Tooltip>
      </div>
    </header>
  </div>
</template>

<style scoped>
.popover-enter-active,
.popover-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}
.popover-enter-from,
.popover-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>
