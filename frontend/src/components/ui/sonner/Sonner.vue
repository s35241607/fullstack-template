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
          'group toast group-[.toaster]:bg-popover group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-2xl group-[.toaster]:px-4 group-[.toaster]:py-3 group-[.toaster]:rounded-xl group-[.toaster]:ring-1 group-[.toaster]:ring-border/50',
        description: 'group-[.toast]:text-muted-foreground group-[.toast]:text-xs',
        actionButton:
          'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
        cancelButton:
          'group-[.toast]:bg-muted group-[.toast]:text-muted-foreground',
        closeButton:
          'group-[.toast]:left-auto group-[.toast]:right-1 group-[.toast]:top-1 group-[.toast]:bg-popover group-[.toast]:text-muted-foreground group-[.toast]:border-border group-[.toast]:hover:text-foreground group-[.toast]:transition-colors group-[.toast]:size-5 group-[.toast]:flex group-[.toast]:items-center group-[.toast]:justify-center group-[.toast]:rounded-full',
      },
    }"
  />
</template>
