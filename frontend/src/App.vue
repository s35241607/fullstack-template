<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
import { Toaster } from 'vue-sonner'
</script>

<template>
  <Toaster position="top-right" rich-colors close-button />
  <AppLayout>
    <RouterView />
  </AppLayout>
</template>
