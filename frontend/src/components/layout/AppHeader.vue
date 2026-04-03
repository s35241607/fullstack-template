<script setup lang="ts">
  import { ref } from 'vue'
  import { Menu, Search, Sun, Moon, X, Home, ChevronRight } from 'lucide-vue-next'
  import { useDark, useToggle } from '@vueuse/core'
  import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
  import NotificationPanel from '@/components/layout/NotificationPanel.vue'

  defineEmits<{
    toggleSidebar: []
  }>()

  const isDark = useDark()
  const toggleDark = useToggle(isDark)
  const { breadcrumbs } = useBreadcrumbs()

  const searchOpen = ref(false)
  const searchQuery = ref('')

  function closeSearch() {
    searchOpen.value = false
    searchQuery.value = ''
  }

  function onSearchKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') closeSearch()
  }
</script>

<template>
  <div class="shrink-0">
    <header class="flex items-center h-14 px-4 gap-3 border-b border-border bg-card shadow-sm">
      <!-- Mobile sidebar toggle -->
      <button
        class="md:hidden p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        aria-label="Toggle sidebar"
        @click="$emit('toggleSidebar')"
      >
        <Menu :size="20" />
      </button>

      <!-- Breadcrumbs -->
      <nav
        class="flex items-center gap-1 text-sm flex-1 min-w-0 overflow-hidden"
        aria-label="Breadcrumb"
      >
        <!-- Home icon always visible -->
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
        <!-- Search (md+) -->
        <div class="hidden md:flex items-center">
          <Transition name="search-expand" mode="out-in">
            <div
              v-if="searchOpen"
              key="open"
              class="flex items-center gap-2 bg-background border border-border rounded-md px-3 py-1.5 w-52"
            >
              <Search :size="14" class="text-muted-foreground shrink-0" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search..."
                class="flex-1 bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground min-w-0"
                autofocus
                @keydown="onSearchKeydown"
              />
              <button
                class="text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Close search"
                @click="closeSearch"
              >
                <X :size="13" />
              </button>
            </div>

            <button
              v-else
              key="closed"
              class="flex items-center gap-2 px-2.5 py-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors text-sm"
              aria-label="Open search"
              @click="searchOpen = true"
            >
              <Search :size="16" />
              <span class="hidden lg:inline text-xs">Search</span>
              <kbd
                class="hidden lg:inline-flex items-center text-[10px] bg-muted px-1.5 py-0.5 rounded border border-border/60 font-mono text-muted-foreground"
              >
                ⌘K
              </kbd>
            </button>
          </Transition>
        </div>

        <!-- Search icon (mobile) -->
        <button
          class="md:hidden p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          :aria-label="searchOpen ? 'Close search' : 'Open search'"
          @click="searchOpen = !searchOpen"
        >
          <X v-if="searchOpen" :size="18" />
          <Search v-else :size="18" />
        </button>

        <!-- Notifications -->
        <NotificationPanel />

        <!-- Theme toggle -->
        <button
          class="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleDark()"
        >
          <Sun v-if="isDark" :size="18" />
          <Moon v-else :size="18" />
        </button>

        <!-- Divider -->
        <div class="w-px h-5 bg-border mx-1"></div>

        <!-- User avatar -->
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
      </div>
    </header>

    <!-- Mobile search bar -->
    <Transition name="slide-down">
      <div
        v-if="searchOpen"
        class="md:hidden flex items-center gap-2 px-4 py-2.5 bg-card border-b border-border"
      >
        <Search :size="14" class="text-muted-foreground shrink-0" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="flex-1 bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground"
          autofocus
          @keydown="onSearchKeydown"
        />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  .search-expand-enter-active,
  .search-expand-leave-active {
    transition:
      opacity 0.15s ease,
      width 0.2s ease;
    overflow: hidden;
  }
  .search-expand-enter-from,
  .search-expand-leave-to {
    opacity: 0;
    width: 0;
  }

  .slide-down-enter-active,
  .slide-down-leave-active {
    transition:
      max-height 0.2s ease,
      opacity 0.15s ease;
    overflow: hidden;
    max-height: 60px;
  }
  .slide-down-enter-from,
  .slide-down-leave-to {
    max-height: 0;
    opacity: 0;
  }
</style>
