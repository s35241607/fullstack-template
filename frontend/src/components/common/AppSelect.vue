<script setup lang="ts">
  import type { HTMLAttributes } from 'vue'
  import { computed } from 'vue'
  import { cn } from '@/lib/utils'
  import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
  } from '@/components/ui/select'
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

  export interface SelectOption {
    label: string
    value: string
    description?: string
    avatar?: string
    disabled?: boolean
  }

  const props = withDefaults(
    defineProps<{
      class?: HTMLAttributes['class']
      modelValue?: string
      options: SelectOption[]
      placeholder?: string
      groupLabel?: string
      disabled?: boolean
    }>(),
    {
      placeholder: '請選擇…',
    },
  )

  const emit = defineEmits<{
    'update:modelValue': [value: string]
  }>()

  const selectedOption = computed(() => props.options.find((opt) => opt.value === props.modelValue))

  const hasAvatars = computed(() => props.options.some((opt) => opt.avatar))
  const hasDescriptions = computed(() => props.options.some((opt) => opt.description))
</script>

<template>
  <Select
    :model-value="modelValue"
    :disabled="disabled"
    @update:model-value="emit('update:modelValue', $event as string)"
  >
    <SelectTrigger
      :class="
        cn(
          'w-full ring-offset-background focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 data-[state=open]:ring-2 data-[state=open]:ring-ring data-[state=open]:ring-offset-2',
          hasAvatars && 'h-12',
          !modelValue && 'text-muted-foreground',
          props.class,
        )
      "
    >
      <!-- Custom trigger content when we have rich options -->
      <template v-if="selectedOption && (selectedOption.avatar || selectedOption.description)">
        <div class="flex items-center gap-2.5 truncate">
          <Avatar v-if="selectedOption.avatar" size="sm" class="h-7 w-7 shrink-0">
            <AvatarImage :src="selectedOption.avatar" :alt="selectedOption.label" />
            <AvatarFallback class="text-[10px]">
              {{ selectedOption.label.substring(0, 2).toUpperCase() }}
            </AvatarFallback>
          </Avatar>
          <div class="flex flex-col items-start leading-tight truncate">
            <span class="truncate text-sm">{{ selectedOption.label }}</span>
            <span
              v-if="selectedOption.description"
              class="truncate text-[11px] text-muted-foreground"
            >
              {{ selectedOption.description }}
            </span>
          </div>
        </div>
      </template>
      <SelectValue v-else :placeholder="placeholder" />
    </SelectTrigger>

    <SelectContent>
      <SelectGroup>
        <SelectLabel v-if="groupLabel">{{ groupLabel }}</SelectLabel>
        <SelectItem
          v-for="opt in options"
          :key="opt.value"
          :value="opt.value"
          :disabled="opt.disabled"
          :class="cn(hasAvatars && 'py-2.5', hasDescriptions && 'py-2.5')"
        >
          <div class="flex items-center gap-2.5">
            <Avatar v-if="opt.avatar" size="sm" class="h-7 w-7 shrink-0">
              <AvatarImage :src="opt.avatar" :alt="opt.label" />
              <AvatarFallback class="text-[10px]">
                {{ opt.label.substring(0, 2).toUpperCase() }}
              </AvatarFallback>
            </Avatar>
            <div class="flex flex-col leading-tight">
              <span class="text-sm">{{ opt.label }}</span>
              <span v-if="opt.description" class="text-[11px] text-muted-foreground">
                {{ opt.description }}
              </span>
            </div>
          </div>
        </SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
