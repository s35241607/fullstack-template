<script setup lang="ts">
  import { ref, computed, nextTick, watch } from 'vue'
  import { Check, Search } from 'lucide-vue-next'
  import type { SearchableSelectEditorParams } from './types'

  const props = defineProps<{ params: SearchableSelectEditorParams }>()

  const options = computed(() => props.params.values ?? [])
  const currentValue = ref<string>(String(props.params.value ?? ''))
  const searchText = ref('')
  const highlightIndex = ref(0)
  const inputRef = ref<HTMLInputElement | null>(null)
  const listRef = ref<HTMLElement | null>(null)

  const filteredOptions = computed(() => {
    const q = searchText.value.toLowerCase().trim()
    if (!q) return options.value
    return options.value.filter((v) => v.toLowerCase().includes(q))
  })

  // Reset highlight to top when search changes
  watch(searchText, () => {
    highlightIndex.value = 0
  })

  const scrollToHighlighted = () => {
    nextTick(() => {
      const list = listRef.value
      if (!list) return
      const item = list.children[highlightIndex.value] as HTMLElement | undefined
      item?.scrollIntoView({ block: 'nearest' })
    })
  }

  const selectOption = (val: string) => {
    currentValue.value = val
    props.params.stopEditing()
  }

  // Keyboard handler on the input — stopPropagation so AG Grid doesn't
  // also handle Arrow / Enter when the popup is open.
  const onKeyDown = (event: KeyboardEvent) => {
    const opts = filteredOptions.value
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        event.stopPropagation()
        highlightIndex.value = Math.min(highlightIndex.value + 1, opts.length - 1)
        scrollToHighlighted()
        break
      case 'ArrowUp':
        event.preventDefault()
        event.stopPropagation()
        highlightIndex.value = Math.max(highlightIndex.value - 1, 0)
        scrollToHighlighted()
        break
      case 'Enter':
        event.preventDefault()
        event.stopPropagation()
        if (opts[highlightIndex.value] !== undefined) {
          selectOption(opts[highlightIndex.value])
        } else {
          props.params.stopEditing()
        }
        break
      case 'Escape':
        event.preventDefault()
        event.stopPropagation()
        props.params.stopEditing(true)
        break
      case 'Tab':
        if (opts[highlightIndex.value] !== undefined) {
          currentValue.value = opts[highlightIndex.value]
        }
        props.params.stopEditing()
        break
    }
  }

  // AG Grid calls afterGuiAttached() once the popup is positioned and visible.
  const afterGuiAttached = () => {
    // Pre-select highlight on current value
    const idx = options.value.indexOf(currentValue.value)
    highlightIndex.value = idx >= 0 ? idx : 0
    nextTick(() => {
      inputRef.value?.focus()
      scrollToHighlighted()
    })
  }

  defineExpose({
    getValue: () => currentValue.value,
    afterGuiAttached,
  })
</script>

<template>
  <!--
    Uses shadcn-vue design tokens (bg-popover, border-border, bg-accent, etc.)
    but is a fully manual implementation to avoid conflicts with reka-ui inside
    AG Grid's popup editor container.
  -->
  <div
    class="w-52 overflow-hidden rounded-md border border-border bg-popover text-popover-foreground shadow-md"
  >
    <!-- Search row -->
    <div class="flex items-center border-b border-border px-3">
      <Search class="mr-2 h-4 w-4 shrink-0 opacity-50" />
      <input
        ref="inputRef"
        v-model="searchText"
        type="text"
        autocomplete="off"
        placeholder="搜尋..."
        class="flex h-9 w-full bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground"
        @keydown="onKeyDown"
      />
    </div>

    <!-- Options list -->
    <div ref="listRef" class="max-h-48 overflow-y-auto p-1">
      <p v-if="filteredOptions.length === 0" class="py-6 text-center text-sm text-muted-foreground">
        無符合選項
      </p>
      <div
        v-for="(opt, i) in filteredOptions"
        :key="opt"
        class="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors"
        :class="
          i === highlightIndex
            ? 'bg-accent text-accent-foreground'
            : 'text-popover-foreground hover:bg-accent hover:text-accent-foreground'
        "
        @mousedown.prevent="selectOption(opt)"
        @mouseover="highlightIndex = i"
      >
        <Check
          class="mr-2 h-4 w-4 shrink-0 transition-opacity"
          :class="opt === currentValue ? 'opacity-100' : 'opacity-0'"
        />
        {{ opt }}
      </div>
    </div>
  </div>
</template>
