<script setup lang="ts">
  import AppLayout from '@/components/layout/AppLayout.vue'
  import AlertDialog from '@/components/ui/alert-dialog/AlertDialog.vue'
  import { Toaster } from '@/components/ui/sonner'
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
  <!--
    Toast: bottom-right, expand=false gives the 3D stacked card effect.
    The stacking/depth is sonner's default behavior when multiple toasts
    are queued and expand is off.
  -->
  <Toaster
    position="bottom-right"
    rich-colors
    close-button
    :theme="toastTheme"
    :expand="false"
    :duration="3000"
    :visible-toasts="5"
    :offset="20"
  />

  <!-- Global confirmation modal — driven by the useConfirm() singleton -->
  <AlertDialog />

  <AppLayout>
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </AppLayout>
</template>
