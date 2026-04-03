<script setup lang="ts">
/**
 * AlertDialog — handles confirmation modals globally.
 * Follows shadcn naming and styles.
 */
import { computed } from 'vue'
import { AlertTriangle, Trash2, X } from 'lucide-vue-next'
import { useConfirm } from '@/composables/useConfirm'
import { cn } from '@/lib/utils'

interface Props {
  class?: string
}

defineProps<Props>()

const { isOpen, options, handleConfirm, handleCancel } = useConfirm()

const isDestructive = computed(() => options.value.variant === 'destructive')
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm-fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[9998] flex items-center justify-center p-4"
        @mousedown.self="handleCancel"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="handleCancel"
        />

        <!-- Dialog -->
        <Transition name="confirm-pop">
          <div
            v-if="isOpen"
            :class="cn(
              'relative z-10 w-full max-w-sm bg-card border border-border rounded-2xl shadow-2xl overflow-hidden',
              $props.class
            )"
            role="alertdialog"
            aria-modal="true"
          >
            <!-- Header -->
            <div class="flex items-start gap-4 p-6 pb-4 text-left">
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
                <h2 class="text-base font-semibold text-foreground leading-tight">
                  {{ options.title }}
                </h2>
                <p class="mt-1.5 text-sm text-muted-foreground leading-relaxed">
                  {{ options.message }}
                </p>
              </div>

              <!-- Close button -->
              <button
                class="text-muted-foreground hover:text-foreground transition-colors shrink-0 -mt-1 -mr-1"
                aria-label="Close"
                @click="handleCancel"
              >
                <X :size="16" />
              </button>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 justify-end px-6 py-4 bg-muted/20 border-t border-border">
              <button
                class="px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors outline-none"
                @click="handleCancel"
              >
                {{ options.cancelText ?? '取消' }}
              </button>
              <button
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors outline-none"
                :class="
                  isDestructive
                    ? 'bg-destructive text-destructive-foreground hover:opacity-90'
                    : 'bg-primary text-primary-foreground hover:opacity-90'
                "
                @click="handleConfirm"
              >
                {{ options.confirmText ?? '確認' }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 0.2s ease;
}
.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-pop-enter-active,
.confirm-pop-leave-active {
  transition:
    transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.15s ease;
}
.confirm-pop-enter-from,
.confirm-pop-leave-to {
  transform: scale(0.9) translateY(8px);
  opacity: 0;
}
</style>
