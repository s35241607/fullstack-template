<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAsyncState } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { bpmnApi } from '@/services/api'
import {
  ArrowLeft, CheckCircle2, XCircle, Play, Clock, Workflow,
  GitMerge, Loader2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id as string)

const { state: definition, isLoading, error, execute: refresh } = useAsyncState(
  () => bpmnApi.getDefinition(id.value),
  null,
  { immediate: true },
)

async function handleToggleActive() {
  if (!definition.value) return
  try {
    await bpmnApi.updateDefinition(id.value, { is_active: !definition.value.is_active })
    toast.success(definition.value.is_active ? 'Process deactivated' : 'Process activated')
    await refresh()
  } catch (err) {
    toast.error('Failed to update', { description: err instanceof Error ? err.message : 'Unknown error' })
  }
}

async function handleStart() {
  if (!definition.value?.is_active) return
  try {
    const instance = await bpmnApi.startProcess(id.value, {
      name: `Run of ${definition.value.name}`,
      started_by: 'current_user',
    })
    toast.success('Process started!', { description: `Instance ID: ${instance.id.slice(0, 8)}…` })
    void router.push('/bpmn/instances')
  } catch (err) {
    toast.error('Failed to start process', { description: err instanceof Error ? err.message : 'Unknown error' })
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div class="space-y-6 max-w-4xl">
    <!-- Back + header -->
    <div class="flex items-center gap-3">
      <button
        class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
        @click="router.back()"
      >
        <ArrowLeft :size="14" />
        Back
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-4 animate-pulse">
      <div class="h-7 w-1/3 rounded bg-muted" />
      <div class="h-4 w-1/2 rounded bg-muted" />
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
    >
      {{ error instanceof Error ? error.message : String(error) }}
    </div>

    <template v-else-if="definition">
      <!-- Title row -->
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <h1 class="text-2xl font-bold text-foreground tracking-tight">{{ definition.name }}</h1>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border"
              :class="definition.is_active
                ? 'bg-success/10 text-success border-success/20'
                : 'bg-muted text-muted-foreground border-border'"
            >
              {{ definition.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <p v-if="definition.description" class="text-sm text-muted-foreground">{{ definition.description }}</p>
          <p v-else class="text-sm text-muted-foreground/50 italic">No description</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm border border-border transition-colors"
            :class="definition.is_active
              ? 'text-warning hover:bg-warning/10'
              : 'text-success hover:bg-success/10'"
            @click="handleToggleActive"
          >
            <CheckCircle2 v-if="!definition.is_active" :size="14" />
            <XCircle v-else :size="14" />
            {{ definition.is_active ? 'Deactivate' : 'Activate' }}
          </button>
          <button
            :disabled="!definition.is_active"
            class="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            @click="handleStart"
          >
            <Play :size="14" />
            Start Process
          </button>
        </div>
      </div>

      <!-- Meta -->
      <div class="flex items-center gap-4 text-xs text-muted-foreground">
        <span class="flex items-center gap-1.5"><Clock :size="12" /> v{{ definition.version }}</span>
        <span class="flex items-center gap-1.5"><Workflow :size="12" /> {{ definition.tasks.length }} tasks</span>
        <span class="flex items-center gap-1.5"><GitMerge :size="12" /> {{ definition.transitions.length }} flows</span>
        <span>Updated {{ formatDate(definition.updated_at) }}</span>
      </div>

      <!-- Tasks -->
      <div class="rounded-xl border border-border bg-card overflow-hidden">
        <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-foreground">Tasks</h2>
          <span class="text-xs text-muted-foreground">{{ definition.tasks.length }} total</span>
        </div>

        <div v-if="definition.tasks.length === 0" class="flex flex-col items-center justify-center py-10 text-muted-foreground gap-2">
          <Workflow :size="24" />
          <p class="text-sm">No tasks defined yet.</p>
        </div>

        <ul v-else class="divide-y divide-border">
          <li
            v-for="task in definition.tasks"
            :key="task.id"
            class="flex items-center gap-4 px-5 py-3.5"
          >
            <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 text-primary shrink-0 text-xs font-semibold">
              {{ task.task_type.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-foreground">{{ task.name }}</p>
              <p class="text-xs text-muted-foreground">{{ task.task_type }}</p>
            </div>
            <div class="text-xs text-muted-foreground shrink-0">
              x: {{ task.position_x }}, y: {{ task.position_y }}
            </div>
          </li>
        </ul>
      </div>

      <!-- Transitions -->
      <div class="rounded-xl border border-border bg-card overflow-hidden">
        <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-foreground">Flows</h2>
          <span class="text-xs text-muted-foreground">{{ definition.transitions.length }} total</span>
        </div>

        <div v-if="definition.transitions.length === 0" class="flex flex-col items-center justify-center py-10 text-muted-foreground gap-2">
          <GitMerge :size="24" />
          <p class="text-sm">No flows defined yet.</p>
        </div>

        <ul v-else class="divide-y divide-border">
          <li
            v-for="t in definition.transitions"
            :key="t.id"
            class="flex items-center gap-3 px-5 py-3"
          >
            <Loader2 :size="12" class="text-muted-foreground shrink-0" />
            <span class="text-sm text-muted-foreground font-mono text-xs truncate">
              {{ t.source_task_id.slice(0, 8) }}… → {{ t.target_task_id.slice(0, 8) }}…
            </span>
            <span v-if="t.label" class="ml-auto text-xs text-muted-foreground italic shrink-0">{{ t.label }}</span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>
