<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { User, LogOut, Settings } from 'lucide-vue-next'
  import {
    Avatar,
    AvatarFallback,
    AvatarImage,
  } from '@/components/ui/avatar'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
  } from '@/components/ui/tooltip'

  // User profile logic
  const userAvatar = ref('https://avatars.githubusercontent.com/u/70700407?v=4&size=64')
  const userName = ref('Admin')
  const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
</script>

<template>
  <Tooltip>
    <TooltipTrigger as-child>
      <div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Avatar size="header" class="border-2 border-transparent hover:border-accent shadow-sm hover:scale-105 active:scale-95 transition-all cursor-pointer">
              <AvatarImage :src="userAvatar" alt="Avatar" />
              <AvatarFallback>{{ userInitial }}</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent :side-offset="8" align="end" class="w-56 p-0 border-border shadow-lg overflow-hidden">
            <DropdownMenuLabel class="px-4 py-3 bg-muted/30 border-b border-border">{{ $t('header.myAccount') }}</DropdownMenuLabel>
            <div class="p-1">
              <DropdownMenuItem>
                <User />
                <span>{{ $t('common.profile') }}</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings />
                <span>{{ $t('common.settings') }}</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem class="text-destructive focus:bg-destructive focus:text-destructive-foreground">
                <LogOut />
                <span>{{ $t('common.logout') }}</span>
              </DropdownMenuItem>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </TooltipTrigger>
    <TooltipContent side="bottom">{{ $t('header.accountTooltip') }}</TooltipContent>
  </Tooltip>
</template>
