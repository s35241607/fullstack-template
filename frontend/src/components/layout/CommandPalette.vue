<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { onKeyStroke } from '@vueuse/core'

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { appNavGroups } from '@/config/navigation'

const router = useRouter()
const { t } = useI18n()
const isOpen = ref(false)

// ── Global Ctrl+K Shortcut ──────────────────────────────────────────
onKeyStroke(['k', 'K'], (e) => {
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault()
    isOpen.value = !isOpen.value
  }
})

interface NavItem {
  id: string
  label: string
  description: string
  icon: unknown
  route: string
  group: string
}

// groupKey → translated group label, items have translated label/description
const groupedPages = computed<{ label: string; items: NavItem[] }[]>(() => {
  return appNavGroups.map((group) => {
    const groupLabel = t(group.label)
    return {
      label: groupLabel,
      items: group.items.map((item) => ({
        id: item.id,
        label: t(item.name),
        description: t(item.description),
        icon: item.icon,
        route: item.path,
        group: groupLabel,
      })),
    }
  })
})

const handleSelect = (item: NavItem) => {
  isOpen.value = false
  router.push(item.route)
}

const openCommandPalette = () => {
  isOpen.value = true
}

onMounted(() => {
  window.addEventListener('app:command-open', openCommandPalette)
})

onUnmounted(() => {
  window.removeEventListener('app:command-open', openCommandPalette)
})
</script>

<template>
  <CommandDialog v-model:open="isOpen">
    <CommandInput :placeholder="$t('command.placeholder')" />
    <CommandList>
      <CommandEmpty>{{ $t('command.empty') }}</CommandEmpty>
      <CommandGroup v-for="group in groupedPages" :key="group.label" :heading="group.label">
        <CommandItem
          v-for="item in group.items"
          :key="item.id"
          :value="item.label"
          @select="() => handleSelect(item)"
        >
          <component :is="item.icon" class="mr-2 h-4 w-4 text-muted-foreground" />
          <div class="flex flex-col">
            <span>{{ item.label }}</span>
            <span class="text-xs text-muted-foreground">{{ item.description }}</span>
          </div>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </CommandDialog>
</template>
