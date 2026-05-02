<script setup lang="ts">
  import { Globe, Check } from 'lucide-vue-next'
  import { useLocale, supportedLocales } from '@/composables/useLocale'
  import { Button } from '@/components/ui/button'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
  } from '@/components/ui/tooltip'

  const { locale, setLocale } = useLocale()
</script>

<template>
  <Tooltip>
    <TooltipTrigger as-child>
      <div>
        <DropdownMenu :modal="false">
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon-sm" aria-label="Switch language">
              <Globe />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent :side-offset="8" align="end" class="w-44 p-0 border-border shadow-lg overflow-hidden">
            <DropdownMenuLabel class="px-4 py-3 text-sm font-semibold bg-muted/30 border-b border-border">
              {{ $t('header.langTooltip') }}
            </DropdownMenuLabel>
            <div class="p-1">
              <DropdownMenuItem
                v-for="loc in supportedLocales"
                :key="loc.value"
                class="gap-2"
                @click="setLocale(loc.value)"
              >
                <Check class="h-3.5 w-3.5" :class="locale === loc.value ? 'opacity-100' : 'opacity-0'" />
                <span>{{ loc.label }}</span>
              </DropdownMenuItem>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </TooltipTrigger>
    <TooltipContent side="bottom">{{ $t('header.langTooltip') }}</TooltipContent>
  </Tooltip>
</template>
