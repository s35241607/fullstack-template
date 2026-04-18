<script lang="ts" setup>
import { Toaster as Sonner, type ToasterProps } from "vue-sonner"
import { useDark } from "@vueuse/core"

const props = defineProps<ToasterProps>()

const isDark = useDark()
</script>

<template>
  <Sonner
    class="toaster group"
    v-bind="props"
    :theme="isDark ? 'dark' : 'light'"
    :toast-options="{
      classes: {
        toast:
          'group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg group-[.toaster]:font-sans',
        description: 'group-[.toast]:text-muted-foreground',
        actionButton:
          'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
        cancelButton:
          'group-[.toast]:bg-muted group-[.toast]:text-muted-foreground',
        closeButton:
          'group-[.toast]:bg-background group-[.toast]:text-muted-foreground group-[.toast]:border-border group-[.toast]:hover:bg-accent group-[.toast]:hover:text-foreground group-[.toast]:transition-colors',
      },
    }"
  />
</template>
