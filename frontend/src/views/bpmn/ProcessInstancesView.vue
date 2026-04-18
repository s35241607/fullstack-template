<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { bpmnApi, type ProcessInstance } from '@/services/api'
import { RefreshCw, XCircle, Loader2, GitFork, ChevronRight } from 'lucide-vue-next'

const filterStatus = ref<string>('')
const cancellingId = ref<string | null>(null)
const expandedId = ref<string | null>(null)

const { state: instances, isLoading, execute: refresh } = useAsyncState(
  async () => bpmnApi.listInstances(),
  [] as ProcessInstance[],
  { immediate: true },
)

const filtered = computed(() =>
  filterStatus.value
    ? instances.value.filter((i) => i.status === filterStatus.value)
    : instances.value,
)

async function handleCancel(instance: ProcessInstance) {
  if (!confirm(`Cancel instance "${instance.name}"?`)) return
  cancellingId.value = instance.id
  try {
    await bpmnApi.cancelInstance(instance.id)
    toast.success('Instance cancelled')
    await refresh()
  } catch (err) {
    toast.error('Failed to cancel', { description: err instanceof Error ? err.message : 'Unknown error' })
  } finally {
    cancellingId.value = null
  }
}

const statusConfig: Record<string, { label: string; classes: string }> = {
  RUNNING: { label: 'Running', classes: 'bg-primary/10 text-primary border-primary/20' },
  COMPLETED: { label: 'Completed', classes: 'bg-success/10 text-success border-success/20' },
  CANCELLED: { label: 'Cancelled', classes: 'bg-muted text-muted-foreground border-border' },
  ERROR: { label: 'Error', classes: 'bg-destructive/10 text-destructive border-destructive/20' },
}

const taskStatusConfig: Record<string, { classes: string }> = {
  PENDING: { classes: 'bg-muted text-muted-foreground' },
  ACTIVE: { classes: 'bg-primary/10 text-primary' },
  COMPLETED: { classes: 'bg-success/10 text-success' },
  SKIPPED: { classes: 'bg-muted text-muted-foreground opacity-60' },
}

function formatDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">Process Instances</h1>
        <p class="text-sm text-muted-foreground mt-1">Monitor and manage running workflow instances.</p>
      </div>
      <div class="flex items-center gap-2">
        <!-- Status filter -->
        <label for="instance-status-filter" class="sr-only">Filter by status</label>
        <select
          id="instance-status-filter"
          v-model="filterStatus"
          name="status_filter"
          autocomplete="off"
          class="rounded-md border border-border bg-background px-2.5 py-1.5 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="">All statuses</option>
          <option value="RUNNING">Running</option>
          <option value="COMPLETED">Completed</option>
          <option value="CANCELLED">Cancelled</option>
          <option value="ERROR">Error</option>
        </select>
        <button
          class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
          :disabled="isLoading"
          @click="() => { void refresh() }"
        >
          <RefreshCw :size="14" :class="isLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div
        v-for="(cfg, status) in statusConfig"
        :key="status"
        class="rounded-xl border border-border bg-card px-4 py-3 cursor-pointer hover:bg-accent/50 transition-colors"
        :class="filterStatus === status ? 'ring-2 ring-primary/30' : ''"
        @click="filterStatus = filterStatus === status ? '' : status"
      >
        <p class="text-[11px] text-muted-foreground uppercase tracking-wide font-medium">{{ cfg.label }}</p>
        <p class="text-2xl font-bold text-foreground mt-1">
          {{ instances.filter((i) => i.status === status).length }}
        </p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading && instances.length === 0" class="space-y-3">
      <div v-for="i in 4" :key="i" class="rounded-xl border border-border bg-card p-4 animate-pulse space-y-2">
        <div class="h-4 w-1/3 rounded bg-muted" />
        <div class="h-3 w-1/2 rounded bg-muted" />
      </div>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!isLoading && filtered.length === 0"
      class="flex flex-col items-center justify-center py-20 gap-3 text-center"
    >
      <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-muted text-muted-foreground">
        <GitFork :size="24" />
      </div>
      <p class="text-sm font-semibold text-foreground">No instances found</p>
      <p class="text-xs text-muted-foreground">Start a process from the Processes page to see it here.</p>
    </div>

    <!-- Instance list -->
    <div v-else class="space-y-3">
      <div
        v-for="inst in filtered"
        :key="inst.id"
        class="rounded-xl border border-border bg-card overflow-hidden"
      >
        <!-- Main row -->
        <div
          class="flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-muted/20 transition-colors"
          @click="toggleExpand(inst.id)"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <h3 class="text-sm font-semibold text-foreground truncate">{{ inst.name }}</h3>
              <span
                class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border"
                :class="statusConfig[inst.status]?.classes ?? ''"
              >
                {{ inst.status }}
              </span>
            </div>
            <p class="text-xs text-muted-foreground">
              {{ inst.definition_name || 'Unknown process' }} · Started by {{ inst.started_by }} · {{ formatDate(inst.started_at) }}
            </p>
          </div>

          <!-- Progress -->
          <div class="hidden sm:flex items-center gap-1 shrink-0">
            <div
              v-for="task in inst.task_instances"
              :key="task.id"
              class="w-2 h-2 rounded-full"
              :class="taskStatusConfig[task.status]?.classes ?? 'bg-muted'"
              :title="`${task.task_name}: ${task.status}`"
            />
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 shrink-0" @click.stop>
            <button
              v-if="inst.status === 'RUNNING'"
              :disabled="cancellingId === inst.id"
              class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors border border-border disabled:opacity-50"
              @click="handleCancel(inst)"
            >
              <Loader2 v-if="cancellingId === inst.id" :size="12" class="animate-spin" />
              <XCircle v-else :size="12" />
              Cancel
            </button>
          </div>

          <ChevronRight
            :size="14"
            class="text-muted-foreground/50 transition-transform duration-200"
            :class="expandedId === inst.id ? 'rotate-90' : ''"
          />
        </div>

        <!-- Task details (expanded) -->
        <div v-if="expandedId === inst.id" class="border-t border-border px-5 py-4">
          <h4 class="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Task Progress</h4>
          <div class="space-y-2">
            <div
              v-for="task in inst.task_instances"
              :key="task.id"
              class="flex items-center gap-3 p-3 rounded-lg border border-border/60 bg-muted/20"
            >
              <div
                class="w-2.5 h-2.5 rounded-full shrink-0"
                :class="taskStatusConfig[task.status]?.classes ?? 'bg-muted'"
              />
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-foreground">{{ task.task_name }}</p>
                <p class="text-[10px] text-muted-foreground">{{ task.task_type }}</p>
              </div>
              <span class="text-[10px] text-muted-foreground shrink-0">{{ task.status }}</span>
              <span v-if="task.completed_at" class="text-[10px] text-muted-foreground shrink-0">
                {{ formatDate(task.completed_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
