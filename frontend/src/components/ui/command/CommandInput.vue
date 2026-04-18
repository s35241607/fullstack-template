<script setup lang="ts">
  import type { ListboxFilterProps } from 'reka-ui'
  import type { HTMLAttributes } from 'vue'
  import { reactiveOmit } from '@vueuse/core'
  import { Search } from 'lucide-vue-next'
  import { ListboxFilter, useForwardProps } from 'reka-ui'
  import { cn } from '@/lib/utils'
  import { useCommand } from '.'

  defineOptions({
    inheritAttrs: false,
  })

  const props = defineProps<
    ListboxFilterProps & {
      class?: HTMLAttributes['class']
    }
  >()

  const delegatedProps = reactiveOmit(props, 'class')

  const forwardedProps = useForwardProps(delegatedProps)

  const { filterState } = useCommand()
</script>

<template>
  <div class="flex items-center border-b border-border/40 px-5" cmdk-input-wrapper>
    <Search class="mr-3 h-5 w-5 shrink-0 text-muted-foreground/70" />
    <ListboxFilter
      v-bind="{ ...forwardedProps, ...$attrs }"
      v-model="filterState.search"
      auto-focus
      :class="
        cn(
          'flex h-14 w-full rounded-md bg-transparent py-3 text-base outline-none placeholder:text-muted-foreground/60 disabled:cursor-not-allowed disabled:opacity-50',
          props.class,
        )
      "
    />
    <kbd
      class="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border/50 bg-muted/50 px-1.5 font-mono text-[10px] font-medium text-muted-foreground/70 shadow-sm"
      >ESC</kbd
    >
  </div>
</template>
