<script setup lang="ts">
  import type { HTMLAttributes } from 'vue'
  import { ref, computed } from 'vue'
  import { Check, ChevronsUpDown } from 'lucide-vue-next'
  import { cn } from '@/lib/utils'
  import { Button } from '@/components/ui/button'
  import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
  } from '@/components/ui/command'
  import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'

  export interface AutoCompleteOption {
    label: string
    value: string
    disabled?: boolean
  }

  const props = withDefaults(
    defineProps<{
      class?: HTMLAttributes['class']
      modelValue?: string
      options: AutoCompleteOption[]
      placeholder?: string
      searchPlaceholder?: string
      emptyText?: string
      disabled?: boolean
    }>(),
    {
      placeholder: '請選擇…',
      searchPlaceholder: '搜尋…',
      emptyText: '找不到結果',
    },
  )

  const emit = defineEmits<{
    'update:modelValue': [value: string]
  }>()

  const open = ref(false)

  const selectedLabel = computed(() => {
    const found = props.options.find((opt) => opt.value === props.modelValue)
    return found?.label ?? ''
  })

  function handleSelect(optionValue: string) {
    emit('update:modelValue', optionValue === props.modelValue ? '' : optionValue)
    open.value = false
  }
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" role="combobox" :aria-expanded="open" :disabled="disabled">
        {{ selectedLabel || placeholder }}
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[--reka-popover-trigger-width] p-0">
      <Command>
        <CommandInput :placeholder="searchPlaceholder" />
        <CommandList>
          <CommandEmpty>{{ emptyText }}</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-for="opt in options"
              :key="opt.value"
              :value="opt.label"
              :disabled="opt.disabled"
              @select="handleSelect(opt.value)"
            >
              <Check
                :class="cn('mr-2 h-4 w-4', modelValue === opt.value ? 'opacity-100' : 'opacity-0')"
              />
              {{ opt.label }}
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
