<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
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

const groupedPages = computed<Record<string, NavItem[]>>(() => {
  return appNavGroups.reduce((acc, group) => {
    acc[group.label] = group.items.map((item) => ({
      id: item.id,
      label: item.name,
      description: item.description,
      icon: item.icon,
      route: item.path,
      group: group.label,
    }))
    return acc
  }, {} as Record<string, NavItem[]>)
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
    <CommandInput placeholder="搜尋頁面、指令 (支援 Ctrl+K)..." />
    <CommandList>
      <CommandEmpty>找不到符合的結果。</CommandEmpty>
      <CommandGroup v-for="(items, groupName) in groupedPages" :key="groupName" :heading="groupName">
        <CommandItem
          v-for="item in items"
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
