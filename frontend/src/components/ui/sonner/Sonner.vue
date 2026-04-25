<script lang="ts" setup>
  import { Toaster as Sonner, type ToasterProps } from 'vue-sonner'
  import { useDark } from '@vueuse/core'

  const props = defineProps<ToasterProps>()

  const isDark = useDark()
</script>

<template>
  <Sonner class="toaster group" v-bind="props" :theme="isDark ? 'dark' : 'light'" />
</template>
