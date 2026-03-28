<script setup lang="ts">
import { ref } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { bpmnApi, type ActiveTask } from '@/services/api'
import { RefreshCw, CheckCircle2, ListTodo, Loader2, Clock } from 'lucide-vue-next'

const completingId = ref<string | null>(null)

const { state: tasks, isLoading, execute: refresh } = useAsyncState(
  () => bpmnApi.listActiveTasks(),
  [] as ActiveTask[],
  { immediate: true },
)

async function handleComplete(task: ActiveTask) {
  completingId.value = task.id
  try {
    await bpmnApi.completeTask(task.process_instance_id, task.id, { assignee: 'current_user' })
    toast.success('Task completed!', { description: `"${task.task_name}" was completed.` })
    await refresh()
  } catch (err) {
    toast.error('Failed to complete task', { description: err instanceof Error ? err.message : 'Unknown error' })
  } finally {
    completingId.value = null
  }
}

function formatDate(iso: string | null) {
  if (!iso) return '—'
  const d = new Date(iso)
  const now = Date.now()
  const diff = now - d.getTime()
  if (diff < 60_000) return 'just now'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`
  return d.toLocaleDateString()
}

const taskTypeLabel: Record<string, string> = {
  START_EVENT: 'Start',
  END_EVENT: 'End',
  USER_TASK: 'User Task',
  SERVICE_TASK: 'Service Task',
  EXCLUSIVE_GATEWAY: 'Gateway',
  PARALLEL_GATEWAY: 'Parallel',
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">My Tasks</h1>
        <p class="text-sm text-muted-foreground mt-1">Active tasks assigned to you across all running processes.</p>
      </div>
      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
        :disabled="isLoading"
        @click="() => { void refresh() }"
      >
        <RefreshCw :size="14" :class="isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <!-- Summary badge -->
    <div class="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-primary/5 border border-primary/20 text-sm text-primary font-medium">
      <ListTodo :size="15" />
      {{ tasks.length }} active {{ tasks.length === 1 ? 'task' : 'tasks' }}
    </div>

    <!-- Loading -->
    <div v-if="isLoading && tasks.length === 0" class="space-y-3">
      <div v-for="i in 3" :key="i" class="rounded-xl border border-border bg-card p-4 animate-pulse">
        <div class="h-4 w-1/3 rounded bg-muted mb-2" />
        <div class="h-3 w-1/2 rounded bg-muted" />
      </div>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!isLoading && tasks.length === 0"
      class="flex flex-col items-center justify-center py-24 gap-4 text-center"
    >
      <div class="flex items-center justify-center w-16 h-16 rounded-2xl bg-success/10 text-success">
        <CheckCircle2 :size="28" />
      </div>
      <div>
        <p class="text-base font-semibold text-foreground">All caught up!</p>
        <p class="text-sm text-muted-foreground mt-1">No active tasks assigned to you right now.</p>
      </div>
    </div>

    <!-- Task list -->
    <div v-else class="space-y-3">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="flex items-center gap-4 rounded-xl border border-border bg-card px-5 py-4 hover:shadow-sm transition-shadow"
      >
        <!-- Type indicator -->
        <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 text-primary shrink-0">
          <ListTodo :size="18" />
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-foreground truncate">{{ task.task_name }}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-[11px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground">
              {{ taskTypeLabel[task.task_type] ?? task.task_type }}
            </span>
            <span class="text-xs text-muted-foreground flex items-center gap-1">
              <Clock :size="10" />
              {{ formatDate(task.started_at) }}
            </span>
          </div>
        </div>

        <!-- Action -->
        <button
          :disabled="completingId === task.id"
          class="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity shrink-0"
          @click="handleComplete(task)"
        >
          <Loader2 v-if="completingId === task.id" :size="13" class="animate-spin" />
          <CheckCircle2 v-else :size="13" />
          Complete
        </button>
      </div>
    </div>
  </div>
</template>
