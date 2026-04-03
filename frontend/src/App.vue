<script setup lang="ts">
  import AppLayout from '@/components/layout/AppLayout.vue'
  import { Toaster } from 'vue-sonner'
  import { useDark } from '@vueuse/core'
  import { computed } from 'vue'

  const isDark = useDark()
  const toastTheme = computed(() => (isDark.value ? 'dark' : 'light'))
</script>

<template>
  <Toaster position="top-right" rich-colors close-button :theme="toastTheme" />
  <AppLayout>
    <RouterView />
  </AppLayout>
</template>
