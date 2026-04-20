<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import CommandPalette from './CommandPalette.vue'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { useTheme } from '@/composables/useTheme'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

const { progress } = useGlobalLoading()
const { isNarrow } = useTheme()
</script>

<template>
  <SidebarProvider>
    <!-- Global progress bar -->
    <div
      v-if="progress > 0"
      class="progress-bar z-50 fixed top-0 left-0"
      :style="{ width: `${progress}%`, opacity: progress === 100 ? 0 : 1 }"
    />

    <AppSidebar />
    <CommandPalette />

    <SidebarInset class="relative flex h-svh w-full min-w-0 flex-col overflow-hidden">
      <div class="flex-1 overflow-y-auto">
        <AppHeader />
        
        <div class="p-4 sm:p-6">
          <!--
            Narrow mode: constrain content to max-w-4xl centered.
            Wide mode: override any max-w-* in child view components so
                       content fills the full available width.
          -->
          <div :class="[isNarrow ? 'max-w-4xl mx-auto' : 'layout-wide', 'min-w-0 w-full overflow-hidden flex flex-col']">
            <slot />
          </div>
        </div>
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>

<style scoped>
/* Progress bar CSS */
.progress-bar {
  height: 3px;
  background-color: var(--primary);
  transition: width 0.3s ease, opacity 0.3s ease;
}
</style>
