<script setup lang="ts">
/**
 * ConfirmDialog — handles confirmation modals globally using shadcn components.
 */
import { AlertTriangle, Trash2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useConfirm } from '@/composables/useConfirm'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { cn } from '@/lib/utils'

const { isOpen, options, handleConfirm, handleCancel } = useConfirm()
const isDestructive = computed(() => options.value.variant === 'destructive')
</script>

<template>
  <AlertDialog :open="isOpen" @update:open="(val) => !val && handleCancel()">
    <AlertDialogContent class="max-w-sm">
      <AlertDialogHeader>
        <div class="flex items-start gap-4">
          <!-- Icon -->
          <div
            :class="cn(
              'flex items-center justify-center size-10 rounded-full shrink-0',
              isDestructive ? 'bg-destructive/10' : 'bg-primary/10'
            )"
          >
            <Trash2
              v-if="isDestructive"
              :size="18"
              class="text-destructive font-bold"
            />
            <AlertTriangle v-else :size="18" class="text-primary font-bold" />
          </div>

          <div class="flex-1 min-w-0">
            <AlertDialogTitle class="text-base font-semibold leading-tight">
              {{ options.title }}
            </AlertDialogTitle>
            <AlertDialogDescription class="mt-1.5 text-sm text-muted-foreground leading-relaxed">
              {{ options.message }}
            </AlertDialogDescription>
          </div>
        </div>
      </AlertDialogHeader>

      <AlertDialogFooter class="mt-4 pt-4 border-t gap-2 sm:gap-0">
        <AlertDialogCancel
          class="rounded-lg"
          @click="handleCancel"
        >
          {{ options.cancelText ?? '取消' }}
        </AlertDialogCancel>
        <AlertDialogAction
          class="rounded-lg"
          :class="isDestructive ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90' : ''"
          @click="handleConfirm"
        >
          {{ options.confirmText ?? '確認' }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
