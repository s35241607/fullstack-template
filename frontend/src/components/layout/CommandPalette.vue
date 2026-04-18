<script setup lang="ts">
  import { computed, onMounted, onUnmounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useI18n } from 'vue-i18n'
  import { onKeyStroke } from '@vueuse/core'
  import { ArrowRight } from 'lucide-vue-next'

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

  // ── Group → Color mapping (icon box color per category) ────────────
  const groupColorMap: Record<string, { icon: string; text: string }> = {
    main: { icon: 'bg-blue-500/15 text-blue-500', text: 'text-blue-500' },
    system: { icon: 'bg-violet-500/15 text-violet-500', text: 'text-violet-500' },
  }
  const defaultColor = { icon: 'bg-primary/10 text-primary', text: 'text-primary' }

  function getGroupColor(groupId: string) {
    return groupColorMap[groupId] ?? defaultColor
  }

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
    groupId: string
    group: string
  }

  const groupedPages = computed<{ id: string; label: string; items: NavItem[] }[]>(() => {
    return appNavGroups.map((group) => {
      const groupLabel = t(group.label)
      return {
        id: group.id,
        label: groupLabel,
        items: group.items.map((item) => ({
          id: item.id,
          label: t(item.name),
          description: t(item.description),
          icon: item.icon,
          route: item.path,
          groupId: group.id,
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
    <CommandList class="py-1">
      <CommandEmpty class="py-10 text-center text-sm text-muted-foreground">
        {{ $t('command.empty') }}
      </CommandEmpty>

      <CommandGroup
        v-for="group in groupedPages"
        :key="group.label"
        :heading="group.label"
        :class="getGroupColor(group.id).text"
      >
        <CommandItem
          v-for="item in group.items"
          :key="item.id"
          :value="item.label"
          class="group mx-1 my-0.5 cursor-pointer rounded-lg border border-transparent px-3 py-2 transition-colors hover:border-border/60 hover:bg-accent/80 hover:text-accent-foreground data-[highlighted]:border-border/60 data-[highlighted]:bg-accent/80 data-[highlighted]:text-accent-foreground"
          @select="() => handleSelect(item)"
        >
          <!-- Icon Box -->
          <div
            class="flex items-center justify-center size-8 rounded-md shrink-0 mr-3"
            :class="getGroupColor(item.groupId).icon"
          >
            <component :is="item.icon" class="size-4" />
          </div>

          <!-- Text -->
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">{{ item.label }}</div>
            <div class="text-xs text-muted-foreground truncate">{{ item.description }}</div>
          </div>

          <!-- Right: Group Badge + Arrow (arrow only on highlighted) -->
          <div class="flex items-center gap-2 shrink-0 ml-2">
            <span
              class="text-[11px] px-1.5 py-0.5 rounded-full border border-border/60 text-muted-foreground"
            >
              {{ item.group }}
            </span>
            <ArrowRight
              class="hidden size-3.5 text-muted-foreground group-hover:flex data-[highlighted]:flex"
            />
          </div>
        </CommandItem>
      </CommandGroup>
    </CommandList>

    <!-- Footer -->
    <div
      class="flex items-center gap-4 border-t border-border/40 bg-muted/30 px-4 py-2.5 text-[12px] text-muted-foreground select-none"
    >
      <span class="flex items-center gap-1.5">
        <kbd class="rounded border bg-muted px-1 py-0.5 font-mono text-[10px]">↑↓</kbd>
        {{ $t('command.select') }}
      </span>
      <span class="flex items-center gap-1.5">
        <kbd class="rounded border bg-muted px-1 py-0.5 font-mono text-[10px]">↵</kbd>
        {{ $t('command.go') }}
      </span>
      <span class="flex items-center gap-1.5">
        <kbd class="rounded border bg-muted px-1 py-0.5 font-mono text-[10px]">ESC</kbd>
        {{ $t('command.close') }}
      </span>
    </div>
  </CommandDialog>
</template>
