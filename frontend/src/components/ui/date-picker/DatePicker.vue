<script setup lang="ts">
/**
 * DatePicker — shadcn-styled date picker wrapper.
 * Integrates VueDatePicker with app theme colors and keyboard optimization.
 */
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { computed } from 'vue'
import { useDark } from '@vueuse/core'
import { format, parse, isValid } from 'date-fns'
import { cn } from '@/lib/utils'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  id?: string
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'yyyy-MM-dd',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const isDark = useDark()

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

function parseFn(dateStr: string): Date {
  const tryFormats = ['yyyy-MM-dd', 'yyyyMMdd', 'MM/dd/yyyy', 'dd/MM/yyyy', 'yyyy/MM/dd']
  for (const fmt of tryFormats) {
    const d = parse(dateStr.trim(), fmt, new Date())
    if (isValid(d)) return d
  }
  return new Date(dateStr)
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
    :text-input-options="{
      format: 'yyyy-MM-dd',
      enterSubmit: true,
      tabSubmit: true,
      openMenu: false,
    }"
    :parse-fn="parseFn"
    :placeholder="placeholder"
    :teleport="true"
    :class="cn('app-date-picker', $props.class)"
    @update:model-value="onPickerUpdate"
  />
</template>

<style>
/* 
   We keep the global override class names for the date picker 
   as it needs to override deep internal styles of the 3rd party component.
*/
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
  transition: border-color 0.15s, box-shadow 0.15s;
}
.app-date-picker .dp__input:focus {
  outline: none;
  border-color: hsl(var(--ring));
  box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
}
.app-date-picker .dp__menu {
  background-color: hsl(var(--popover));
  border-color: hsl(var(--border));
  border-radius: var(--radius-lg);
  color: hsl(var(--popover-foreground));
  box-shadow: 0 10px 40px -5px rgba(0, 0, 0, 0.2);
  z-index: 9999;
}
.app-date-picker .dp__cell_inner:hover:not(.dp__active_date) {
  background-color: hsl(var(--accent));
}
.app-date-picker .dp__active_date {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}
.app-date-picker .dp__today {
  border-color: hsl(var(--primary));
}
</style>
