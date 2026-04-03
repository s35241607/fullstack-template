<script setup lang="ts">
import { ref } from 'vue'
import { useMediaQuery } from '@vueuse/core'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { useTheme } from '@/composables/useTheme'

const isDesktop = useMediaQuery('(min-width: 768px)')
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)

const { progress } = useGlobalLoading()
const { isNarrow } = useTheme()

function toggleSidebar() {
  if (isDesktop.value) {
    sidebarCollapsed.value = !sidebarCollapsed.value
  } else {
    mobileSidebarOpen.value = !mobileSidebarOpen.value
  }
}
</script>

<template>
  <div class="flex h-screen bg-background overflow-hidden">
    <!-- Global progress bar -->
    <div
      v-if="progress > 0"
      class="progress-bar"
      :style="{ width: `${progress}%`, opacity: progress === 100 ? 0 : 1 }"
    />

    <!-- Mobile backdrop -->
    <Transition name="fade">
      <div
        v-if="mobileSidebarOpen && !isDesktop"
        class="fixed inset-0 z-20 bg-black/50 backdrop-blur-sm"
        aria-hidden="true"
        @click="mobileSidebarOpen = false"
      />
    </Transition>

    <!-- Desktop sidebar -->
    <div class="hidden md:flex shrink-0 relative z-10 overflow-visible">
      <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    </div>

    <!-- Mobile sidebar (slide-in overlay) -->
    <Transition name="slide">
      <div
        v-if="mobileSidebarOpen"
        class="fixed left-0 top-0 z-30 h-full md:hidden shadow-xl"
      >
        <AppSidebar :collapsed="false" @toggle="mobileSidebarOpen = false" />
      </div>
    </Transition>

    <!-- Main content area -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppHeader @toggle-sidebar="toggleSidebar" />

      <main class="flex-1 overflow-y-auto p-4 sm:p-6">
        <!-- Narrow mode wrapper -->
        <div :class="isNarrow ? 'max-w-5xl mx-auto' : ''">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Backdrop fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Sidebar slide */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
