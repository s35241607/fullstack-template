<script setup lang="ts">
/**
 * AppDatePicker — supports typing, paste, and calendar popover.
 * Uses @vuepic/vue-datepicker (named export: VueDatePicker).
 */

import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { computed } from 'vue'
import { useDark } from '@vueuse/core'
import { format, parse, isValid } from 'date-fns'

const props = withDefaults(
  defineProps<{
    modelValue?: string // YYYY-MM-DD
    placeholder?: string
    disabled?: boolean
    id?: string
  }>(),
  {
    modelValue: '',
    placeholder: 'YYYY-MM-DD',
    disabled: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const isDark = useDark()

// Convert YYYY-MM-DD string → Date object for the picker
const pickerValue = computed<Date | null>(() => {
  if (!props.modelValue) return null
  const d = parse(props.modelValue, 'yyyy-MM-dd', new Date())
  return isValid(d) ? d : null
})

function onPickerUpdate(val: Date | null) {
  if (!val) {
    emit('update:modelValue', '')
    return
  }
  emit('update:modelValue', format(val, 'yyyy-MM-dd'))
}
</script>

<template>
  <VueDatePicker
    :model-value="pickerValue"
    :dark="isDark"
    :disabled="disabled"
    auto-apply
    :enable-time-picker="false"
    format="yyyy-MM-dd"
    text-input
    :text-input-options="{ format: 'yyyy-MM-dd', enterSubmit: true, tabSubmit: true }"
    :placeholder="placeholder"
    :teleport="true"
    class="app-date-picker"
    @update:model-value="onPickerUpdate"
  />
</template>

<style>
/* Override @vuepic/vue-datepicker styles to match app design */
.app-date-picker {
  width: 100%;
}

.app-date-picker .dp__input {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  border-color: hsl(var(--input));
  border-radius: var(--radius);
  font-size: 0.875rem;
  height: 2.5rem;
  padding: 0 2.5rem 0 0.75rem;
  font-family: inherit;
}

.app-date-picker .dp__input:focus {
  outline: none;
  border-color: hsl(var(--ring));
  box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
}

.app-date-picker .dp__input_icon {
  color: hsl(var(--muted-foreground));
}

.app-date-picker .dp__button,
.app-date-picker .dp__action_button {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border-radius: var(--radius);
}

.app-date-picker .dp__calendar_header_item,
.app-date-picker .dp__cell_inner {
  border-radius: var(--radius-sm);
}

.app-date-picker .dp__active_date {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.app-date-picker .dp__today {
  border-color: hsl(var(--primary));
}

.app-date-picker .dp__menu {
  background-color: hsl(var(--popover));
  border-color: hsl(var(--border));
  border-radius: var(--radius-lg);
  color: hsl(var(--popover-foreground));
  box-shadow: 0 10px 40px -5px rgba(0, 0, 0, 0.25);
  z-index: 9999;
}

.app-date-picker .dp__arrow_top,
.app-date-picker .dp__arrow_bottom {
  background-color: hsl(var(--popover));
  border-color: hsl(var(--border));
}

.app-date-picker .dp__calendar_header_item {
  color: hsl(var(--muted-foreground));
  font-size: 0.75rem;
}

.app-date-picker .dp__cell_inner:hover:not(.dp__active_date):not(.dp__today) {
  background-color: hsl(var(--accent));
}
</style>
