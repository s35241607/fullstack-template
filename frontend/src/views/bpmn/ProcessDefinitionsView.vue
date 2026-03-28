<script setup lang="ts">
import { ref } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { bpmnApi, type ProcessDefinition } from '@/services/api'
import {
  Plus, Trash2, Play, Eye, RefreshCw, Loader2, Workflow,
  CheckCircle2, XCircle, AlertCircle, Clock
} from 'lucide-vue-next'

const router = useRouter()

const showCreate = ref(false)
const newName = ref('')
const newDescription = ref('')
const isCreating = ref(false)
const deletingId = ref<string | null>(null)
const startingId = ref<string | null>(null)
const startName = ref('')
const startDialogId = ref<string | null>(null)

const { state: definitions, isLoading, execute: refresh } = useAsyncState(
  () => bpmnApi.listDefinitions(),
  [] as ProcessDefinition[],
  { immediate: true },
)

async function handleCreate() {
  if (!newName.value.trim()) return
  isCreating.value = true
  try {
    await bpmnApi.createDefinition({ name: newName.value.trim(), description: newDescription.value.trim() })
    toast.success('Process created', { description: `"${newName.value.trim()}" is ready to configure.` })
    newName.value = ''
    newDescription.value = ''
    showCreate.value = false
    await refresh()
  } catch (err) {
    toast.error('Failed to create process', { description: err instanceof Error ? err.message : 'Unknown error' })
  } finally {
    isCreating.value = false
  }
}

async function handleDelete(def: ProcessDefinition) {
  if (!confirm(`Delete "${def.name}"? This cannot be undone.`)) return
  deletingId.value = def.id
  try {
    await bpmnApi.deleteDefinition(def.id)
    toast.success('Process deleted')
    await refresh()
  } catch (err) {
    toast.error('Failed to delete', { description: err instanceof Error ? err.message : 'Unknown error' })
  } finally {
    deletingId.value = null
  }
}

async function handleToggleActive(def: ProcessDefinition) {
  try {
    await bpmnApi.updateDefinition(def.id, { is_active: !def.is_active })
    toast.success(def.is_active ? 'Process deactivated' : 'Process activated')
    await refresh()
  } catch (err) {
    toast.error('Failed to update', { description: err instanceof Error ? err.message : 'Unknown error' })
  }
}

function openStartDialog(def: ProcessDefinition) {
  startDialogId.value = def.id
  startName.value = `Run of ${def.name}`
}

async function handleStart() {
  if (!startDialogId.value || !startName.value.trim()) return
  startingId.value = startDialogId.value
  try {
    const instance = await bpmnApi.startProcess(startDialogId.value, {
      name: startName.value.trim(),
      started_by: 'current_user',
    })
    toast.success('Process started!', { description: `Instance ID: ${instance.id.slice(0, 8)}…` })
    startDialogId.value = null
    await router.push('/bpmn/instances')
  } catch (err) {
    toast.error('Failed to start process', { description: err instanceof Error ? err.message : 'Unknown error' })
  } finally {
    startingId.value = null
  }
}

const statusBadge = (active: boolean) =>
  active
    ? 'bg-success/10 text-success border-success/20'
    : 'bg-muted text-muted-foreground border-border'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">Process Definitions</h1>
        <p class="text-sm text-muted-foreground mt-1">Design and manage BPMN workflow processes.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors"
          :disabled="isLoading"
          @click="() => { void refresh() }"
        >
          <RefreshCw :size="14" :class="isLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
        <button
          class="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
          @click="showCreate = true"
        >
          <Plus :size="15" />
          New Process
        </button>
      </div>
    </div>

    <!-- Create dialog -->
    <div v-if="showCreate" class="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
        <h2 class="text-sm font-semibold text-foreground">New Process Definition</h2>
        <button class="text-muted-foreground hover:text-foreground text-sm" @click="showCreate = false">Cancel</button>
      </div>
      <div class="p-5 space-y-3">
        <div>
          <label class="block text-xs font-medium text-foreground mb-1.5">Name <span class="text-destructive">*</span></label>
          <input
            v-model="newName"
            type="text"
            placeholder="e.g. Employee Onboarding"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-foreground mb-1.5">Description</label>
          <textarea
            v-model="newDescription"
            rows="2"
            placeholder="Describe what this process does…"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow resize-none"
          />
        </div>
        <div class="flex justify-end gap-2 pt-1">
          <button
            class="px-3.5 py-1.5 rounded-md border border-border text-sm text-muted-foreground hover:bg-accent transition-colors"
            @click="showCreate = false"
          >
            Cancel
          </button>
          <button
            :disabled="!newName.trim() || isCreating"
            class="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            @click="handleCreate"
          >
            <Loader2 v-if="isCreating" :size="13" class="animate-spin" />
            <Plus v-else :size="13" />
            Create
          </button>
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading && definitions.length === 0" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="i in 3" :key="i" class="rounded-xl border border-border bg-card p-5 space-y-3 animate-pulse">
        <div class="h-4 w-2/3 rounded bg-muted" />
        <div class="h-3 w-full rounded bg-muted" />
        <div class="h-3 w-1/2 rounded bg-muted" />
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="!isLoading && definitions.length === 0"
      class="flex flex-col items-center justify-center py-24 gap-4 text-center"
    >
      <div class="flex items-center justify-center w-16 h-16 rounded-2xl bg-muted text-muted-foreground">
        <Workflow :size="28" />
      </div>
      <div>
        <p class="text-base font-semibold text-foreground">No processes yet</p>
        <p class="text-sm text-muted-foreground mt-1">Create your first BPMN process definition to get started.</p>
      </div>
      <button
        class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
        @click="showCreate = true"
      >
        <Plus :size="15" /> New Process
      </button>
    </div>

    <!-- Process cards -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="def in definitions"
        :key="def.id"
        class="group rounded-xl border border-border bg-card hover:shadow-md transition-shadow overflow-hidden flex flex-col"
      >
        <div class="p-5 flex-1">
          <!-- Title + status -->
          <div class="flex items-start justify-between gap-2 mb-2">
            <h3 class="text-sm font-semibold text-foreground leading-snug line-clamp-2">{{ def.name }}</h3>
            <span
              class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border"
              :class="statusBadge(def.is_active)"
            >
              {{ def.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <p class="text-xs text-muted-foreground line-clamp-2 leading-relaxed mb-3">
            {{ def.description || 'No description provided.' }}
          </p>
          <!-- Stats -->
          <div class="flex items-center gap-3 text-xs text-muted-foreground">
            <span class="flex items-center gap-1">
              <Clock :size="11" />
              v{{ def.version }}
            </span>
            <span class="flex items-center gap-1">
              <CheckCircle2 :size="11" />
              {{ def.tasks.length }} tasks
            </span>
            <span class="flex items-center gap-1">
              <AlertCircle :size="11" />
              {{ def.transitions.length }} flows
            </span>
          </div>
        </div>

        <!-- Actions footer -->
        <div class="border-t border-border px-4 py-2.5 flex items-center gap-1">
          <RouterLink
            :to="`/bpmn/definitions/${def.id}`"
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <Eye :size="13" /> View
          </RouterLink>
          <button
            :disabled="!def.is_active || startingId === def.id"
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            @click="openStartDialog(def)"
          >
            <Loader2 v-if="startingId === def.id" :size="13" class="animate-spin" />
            <Play v-else :size="13" />
            Start
          </button>
          <button
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs transition-colors"
            :class="def.is_active
              ? 'text-warning hover:bg-warning/10'
              : 'text-success hover:bg-success/10'"
            @click="handleToggleActive(def)"
          >
            <CheckCircle2 v-if="!def.is_active" :size="13" />
            <XCircle v-else :size="13" />
            {{ def.is_active ? 'Deactivate' : 'Activate' }}
          </button>
          <div class="flex-1" />
          <button
            :disabled="deletingId === def.id"
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-50"
            @click="handleDelete(def)"
          >
            <Loader2 v-if="deletingId === def.id" :size="13" class="animate-spin" />
            <Trash2 v-else :size="13" />
          </button>
        </div>
      </div>
    </div>

    <!-- Start Process Dialog -->
    <Teleport to="body">
      <div
        v-if="startDialogId"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="startDialogId = null"
      >
        <div class="w-full max-w-md rounded-xl border border-border bg-card shadow-xl">
          <div class="px-5 py-4 border-b border-border">
            <h2 class="text-base font-semibold text-foreground">Start Process</h2>
            <p class="text-sm text-muted-foreground mt-0.5">Give this run a descriptive name.</p>
          </div>
          <div class="p-5 space-y-3">
            <div>
              <label class="block text-xs font-medium text-foreground mb-1.5">Instance Name <span class="text-destructive">*</span></label>
              <input
                v-model="startName"
                type="text"
                class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                autofocus
              />
            </div>
          </div>
          <div class="px-5 pb-4 flex justify-end gap-2">
            <button
              class="px-3.5 py-1.5 rounded-md border border-border text-sm text-muted-foreground hover:bg-accent transition-colors"
              @click="startDialogId = null"
            >
              Cancel
            </button>
            <button
              :disabled="!startName.trim() || !!startingId"
              class="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
              @click="handleStart"
            >
              <Loader2 v-if="startingId" :size="13" class="animate-spin" />
              <Play v-else :size="13" />
              Start
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
