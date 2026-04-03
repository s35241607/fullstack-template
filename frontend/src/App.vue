<script setup lang="ts">
  import AppLayout from '@/components/layout/AppLayout.vue'
  import { Toaster } from 'vue-sonner'
  import { useDark } from '@vueuse/core'
  import { computed, watch } from 'vue'

  const isDark = useDark()

  // Explicitly sync dark class so toast and themes both work
  watch(isDark, (val) => {
    document.documentElement.classList.toggle('dark', val)
  }, { immediate: true })

  const toastTheme = computed(() => (isDark.value ? 'dark' : 'light'))
</script>

<template>
  <Toaster
    position="top-right"
    rich-colors
    close-button
    :theme="toastTheme"
    expand
    :duration="4000"
    :toastOptions="{ style: { zIndex: 99999 } }"
  />
  <AppLayout>
    <RouterView />
  </AppLayout>
</template>
