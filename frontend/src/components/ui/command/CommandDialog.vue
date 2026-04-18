<script setup lang="ts">
  import type { DialogRootEmits, DialogRootProps } from 'reka-ui'
  import { useForwardPropsEmits } from 'reka-ui'
  import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog'
  import Command from './Command.vue'

  const props = defineProps<DialogRootProps>()
  const emits = defineEmits<DialogRootEmits>()

  const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <Dialog v-bind="forwarded">
    <DialogContent
      disable-default-motion
      overlay-class="bg-background/[0.04] backdrop-blur-[3px] supports-[backdrop-filter]:bg-background/[0.02] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 duration-200"
      class="top-[15%] translate-y-0 overflow-hidden border-border/40 bg-background/84 p-0 shadow-2xl backdrop-blur-xl transition-opacity sm:max-w-[700px] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 duration-200 [&>button:last-child]:hidden"
    >
      <DialogTitle class="sr-only">{{ $t('command.title') }}</DialogTitle>
      <DialogDescription class="sr-only">{{ $t('command.description') }}</DialogDescription>
      <Command
        class="rounded-none bg-transparent [&_[cmdk-group-heading]]:px-5 [&_[cmdk-group-heading]]:py-3 [&_[cmdk-group-heading]]:font-bold [&_[cmdk-group-heading]]:text-primary [&_[cmdk-group-heading]]:text-sm [&_[cmdk-group]:not([hidden])_~[cmdk-group]]:pt-0 [&_[cmdk-group]]:px-0"
      >
        <slot />
      </Command>
    </DialogContent>
  </Dialog>
</template>
