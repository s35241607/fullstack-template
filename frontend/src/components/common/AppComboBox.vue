<script setup lang="ts">
  import type { HTMLAttributes } from 'vue'
  import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
  import { Check, ChevronsUpDown, Plus } from 'lucide-vue-next'
  import { cn } from '@/lib/utils'

  export interface ComboBoxOption {
    label: string
    value: string
    disabled?: boolean
  }

  const props = withDefaults(
    defineProps<{
      class?: HTMLAttributes['class']
      modelValue?: string
      options: ComboBoxOption[]
      placeholder?: string
      emptyText?: string
      createText?: string
      disabled?: boolean
      /** Allow creating new entries from free-text input */
      allowCreate?: boolean
    }>(),
    {
      placeholder: '輸入或選擇…',
      emptyText: '找不到符合的選項',
      createText: '新增',
      allowCreate: true,
    },
  )

  const emit = defineEmits<{
    'update:modelValue': [value: string]
    /** Emitted when user creates a new entry via free-text */
    create: [value: string]
  }>()

  // ── Refs ─────────────────────────────────────────────────────────────────────

  const open = ref(false)
  const searchQuery = ref('')
  const wrapperRef = ref<HTMLDivElement | null>(null)
  const inputRef = ref<HTMLInputElement | null>(null)
  const dropdownRef = ref<HTMLDivElement | null>(null)
  const highlightIndex = ref(-1)

  // ── Sync from modelValue ─────────────────────────────────────────────────────

  watch(
    () => props.modelValue,
    (val) => {
      if (!open.value) {
        const found = props.options.find((opt) => opt.value === val)
        searchQuery.value = found ? found.label : (val ?? '')
      }
    },
    { immediate: true },
  )

  // ── Filtered options ─────────────────────────────────────────────────────────

  const filteredOptions = computed(() => {
    if (!searchQuery.value) return props.options
    const q = searchQuery.value.toLowerCase()
    return props.options.filter((opt) => opt.label.toLowerCase().includes(q))
  })

  const isExactMatch = computed(() =>
    props.options.some((opt) => opt.label.toLowerCase() === searchQuery.value.toLowerCase()),
  )

  const showCreateAction = computed(
    () => props.allowCreate && searchQuery.value.trim() !== '' && !isExactMatch.value,
  )

  /** Total selectable items (options + optional create button) */
  const totalItems = computed(() => filteredOptions.value.length + (showCreateAction.value ? 1 : 0))

  // ── Handlers ─────────────────────────────────────────────────────────────────

  function handleInput(event: Event) {
    const value = (event.target as HTMLInputElement).value
    searchQuery.value = value
    emit('update:modelValue', value)
    highlightIndex.value = -1
    if (!open.value) open.value = true
  }

  function handleSelect(opt: ComboBoxOption) {
    searchQuery.value = opt.label
    emit('update:modelValue', opt.value)
    closeDropdown()
  }

  function handleCreate() {
    const trimmed = searchQuery.value.trim()
    if (!trimmed) return
    emit('create', trimmed)
    emit('update:modelValue', trimmed)
    closeDropdown()
  }

  function openDropdown() {
    if (props.disabled) return
    open.value = true
    highlightIndex.value = -1
  }

  function closeDropdown() {
    open.value = false
    highlightIndex.value = -1
  }

  function handleFocus() {
    openDropdown()
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!open.value && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      e.preventDefault()
      openDropdown()
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        highlightIndex.value = Math.min(highlightIndex.value + 1, totalItems.value - 1)
        scrollHighlightedIntoView()
        break
      case 'ArrowUp':
        e.preventDefault()
        highlightIndex.value = Math.max(highlightIndex.value - 1, -1)
        scrollHighlightedIntoView()
        break
      case 'Enter':
        e.preventDefault()
        if (highlightIndex.value >= 0 && highlightIndex.value < filteredOptions.value.length) {
          const opt = filteredOptions.value[highlightIndex.value]
          if (!opt.disabled) handleSelect(opt)
        } else if (
          highlightIndex.value === filteredOptions.value.length &&
          showCreateAction.value
        ) {
          handleCreate()
        } else if (showCreateAction.value) {
          handleCreate()
        }
        break
      case 'Escape':
        e.preventDefault()
        closeDropdown()
        break
      case 'Tab':
        closeDropdown()
        break
    }
  }

  function scrollHighlightedIntoView() {
    nextTick(() => {
      const el = dropdownRef.value?.querySelector('[data-highlighted]') as HTMLElement | null
      el?.scrollIntoView({ block: 'nearest' })
    })
  }

  // ── Click outside ────────────────────────────────────────────────────────────

  function onClickOutside(e: MouseEvent) {
    const target = e.target as Node
    if (wrapperRef.value?.contains(target)) return
    if (dropdownRef.value?.contains(target)) return
    closeDropdown()
  }

  onMounted(() => {
    document.addEventListener('mousedown', onClickOutside)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('mousedown', onClickOutside)
  })

  // ── Dropdown position ────────────────────────────────────────────────────────

  const dropdownStyle = computed(() => {
    // We'll position it absolutely below the input, matching width via CSS
    return {
      top: '100%',
      left: '0',
      right: '0',
      marginTop: '4px',
    }
  })
</script>

<template>
  <div ref="wrapperRef" :class="cn('relative w-full', props.class)">
    <!-- Input -->
    <div class="relative">
      <input
        ref="inputRef"
        :value="searchQuery"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="
          cn(
            'file:text-foreground placeholder:text-muted-foreground dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 pr-8 text-base shadow-xs transition-[color,box-shadow] outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
            'focus:border-ring focus:ring-ring/50 focus:ring-[3px]',
          )
        "
        @input="handleInput"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />
      <ChevronsUpDown
        class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 shrink-0 opacity-40"
      />
    </div>

    <!-- Dropdown -->
    <div
      v-if="open"
      ref="dropdownRef"
      :style="dropdownStyle"
      class="absolute z-50 w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95"
    >
      <!-- Option list -->
      <ul v-if="filteredOptions.length > 0" class="max-h-[200px] overflow-y-auto p-1">
        <li
          v-for="(opt, idx) in filteredOptions"
          :key="opt.value"
          :data-highlighted="highlightIndex === idx ? '' : undefined"
          :class="
            cn(
              'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors',
              highlightIndex === idx && 'bg-accent text-accent-foreground',
              highlightIndex !== idx && 'hover:bg-accent/50',
              opt.disabled && 'pointer-events-none opacity-50',
            )
          "
          @click="!opt.disabled && handleSelect(opt)"
          @mouseenter="highlightIndex = idx"
        >
          <Check
            :class="
              cn('mr-2 h-4 w-4 shrink-0', modelValue === opt.value ? 'opacity-100' : 'opacity-0')
            "
          />
          {{ opt.label }}
        </li>
      </ul>

      <!-- Empty state -->
      <div
        v-if="filteredOptions.length === 0 && !showCreateAction"
        class="px-3 py-4 text-center text-sm text-muted-foreground"
      >
        {{ emptyText }}
      </div>

      <!-- Create new entry action -->
      <div v-if="showCreateAction" class="border-t border-border/40 p-1">
        <button
          :data-highlighted="highlightIndex === filteredOptions.length ? '' : undefined"
          :class="
            cn(
              'flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm transition-colors',
              highlightIndex === filteredOptions.length
                ? 'bg-accent text-accent-foreground'
                : 'text-primary hover:bg-accent/50',
            )
          "
          @click="handleCreate"
          @mouseenter="highlightIndex = filteredOptions.length"
        >
          <Plus class="h-4 w-4 shrink-0" />
          {{ createText }} "<span class="font-semibold">{{ searchQuery.trim() }}</span
          >"
        </button>
      </div>
    </div>
  </div>
</template>
