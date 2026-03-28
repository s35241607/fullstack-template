<script setup lang="ts">
import { useItems } from '@/composables/useItems'
import { ref } from 'vue'
import { Plus, Trash2, RefreshCw, AlertCircle, PackageOpen, Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

const { items, isLoading, error, createItem, deleteItem, refresh } = useItems()

const newName = ref('')
const newDescription = ref('')
const isCreating = ref(false)
const deletingId = ref<string | null>(null)

function handleRefresh() {
  void refresh()
  toast.info('Refreshing items…')
}

async function handleCreate() {
  if (!newName.value.trim()) return
  isCreating.value = true
  try {
    await createItem(newName.value.trim(), newDescription.value.trim())
    toast.success('Item created', { description: `"${newName.value.trim()}" was added.` })
    newName.value = ''
    newDescription.value = ''
  } catch (err) {
    toast.error('Failed to create item', {
      description: err instanceof Error ? err.message : 'Unknown error',
    })
  } finally {
    isCreating.value = false
  }
}

async function handleDelete(id: string, name: string) {
  deletingId.value = id
  try {
    await deleteItem(id)
    toast.success('Item deleted', { description: `"${name}" was removed.` })
  } catch (err) {
    toast.error('Failed to delete item', {
      description: err instanceof Error ? err.message : 'Unknown error',
    })
  } finally {
    deletingId.value = null
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">Items</h1>
        <p class="text-sm text-muted-foreground mt-1">
          Manage items stored in the FastAPI backend.
        </p>
      </div>
      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-border transition-colors shrink-0"
        :disabled="isLoading"
        aria-label="Refresh items"
        @click="handleRefresh"
      >
        <RefreshCw
          :size="14"
          :class="isLoading ? 'animate-spin' : ''"
        />
        <span class="hidden sm:inline">Refresh</span>
      </button>
    </div>

    <!-- Create form -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30">
        <h2 class="text-sm font-medium text-foreground">New item</h2>
      </div>
      <div class="p-4 flex flex-col sm:flex-row gap-2">
        <input
          v-model="newName"
          type="text"
          placeholder="Name *"
          class="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
          @keydown.enter="handleCreate"
        />
        <input
          v-model="newDescription"
          type="text"
          placeholder="Description (optional)"
          class="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
          @keydown.enter="handleCreate"
        />
        <button
          :disabled="!newName.trim() || isCreating"
          class="flex items-center justify-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity shrink-0"
          @click="handleCreate"
        >
          <Loader2 v-if="isCreating" :size="14" class="animate-spin" />
          <Plus v-else :size="14" />
          Add
        </button>
      </div>
    </div>

    <!-- Error state -->
    <div
      v-if="error"
      class="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
    >
      <AlertCircle :size="16" class="shrink-0" />
      <span>{{ error instanceof Error ? error.message : String(error) }}</span>
    </div>

    <!-- List -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
        <h2 class="text-sm font-medium text-foreground">Items</h2>
        <span class="text-xs text-muted-foreground">
          {{ items.length }} {{ items.length === 1 ? 'item' : 'items' }}
        </span>
      </div>

      <!-- Loading skeleton -->
      <div v-if="isLoading && items.length === 0" class="divide-y divide-border">
        <div
          v-for="i in 3"
          :key="i"
          class="flex items-center gap-3 px-5 py-4"
        >
          <div class="h-4 w-4 rounded bg-muted animate-pulse shrink-0"></div>
          <div class="flex-1 space-y-1.5">
            <div class="h-3.5 w-1/3 rounded bg-muted animate-pulse"></div>
            <div class="h-3 w-1/2 rounded bg-muted animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="!isLoading && items.length === 0"
        class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground"
      >
        <div class="flex items-center justify-center w-12 h-12 rounded-full bg-muted">
          <PackageOpen :size="22" />
        </div>
        <div class="text-center">
          <p class="text-sm font-medium text-foreground">No items yet</p>
          <p class="text-xs text-muted-foreground mt-0.5">Create your first item above.</p>
        </div>
      </div>

      <!-- Items list -->
      <ul v-else class="divide-y divide-border">
        <li
          v-for="item in items"
          :key="item.id"
          class="flex items-center gap-4 px-5 py-3.5 hover:bg-muted/30 transition-colors group"
        >
          <div class="flex items-center justify-center w-7 h-7 rounded-md bg-primary/10 text-primary shrink-0 text-xs font-bold">
            {{ item.name.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-foreground truncate">{{ item.name }}</p>
            <p v-if="item.description" class="text-xs text-muted-foreground truncate mt-0.5">
              {{ item.description }}
            </p>
            <p v-else class="text-xs text-muted-foreground/50 italic mt-0.5">No description</p>
          </div>
          <button
            :disabled="deletingId === item.id"
            class="p-1.5 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50 shrink-0"
            :aria-label="`Delete ${item.name}`"
            @click="handleDelete(item.id, item.name)"
          >
            <Loader2 v-if="deletingId === item.id" :size="14" class="animate-spin" />
            <Trash2 v-else :size="14" />
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
