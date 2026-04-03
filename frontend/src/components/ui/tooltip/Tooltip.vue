<script setup lang="ts">
/**
 * Tooltip — a lightweight tooltip component.
 * Follows shadcn composition patterns.
 */
import {
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  TooltipArrow,
} from 'radix-vue'
import { cn } from '@/lib/utils'

interface Props {
  content: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  delayDuration?: number
  disabled?: boolean
  class?: string
}

withDefaults(defineProps<Props>(), {
  side: 'bottom',
  delayDuration: 600,
  disabled: false,
})
</script>

<template>
  <TooltipProvider :delay-duration="delayDuration">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal v-if="!disabled">
        <TooltipContent
          :side="side"
          :side-offset="6"
          :class="cn(
            'z-[9999] bg-popover text-popover-foreground border border-border rounded-md px-2 py-1 text-xs shadow-md select-none',
            $props.class
          )"
        >
          {{ content }}
          <TooltipArrow class="fill-border" />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>
