# Frontend Code Conventions

This is the authoritative reference for the project's frontend conventions.
Stack: Vue 3.5 · TypeScript 5 · Tailwind CSS v4 · shadcn-vue (radix-vue) · Pinia · VueUse · Axios

---

## Component Rules

### File Structure (always in this order)
```vue
<script setup lang="ts">
// 1. vue imports (ref, computed, onMounted, etc.)
// 2. @vueuse/core
// 3. @/composables/...
// 4. @/services/api  (only in Views, not generic components)
// 5. @/stores/...    (only if truly global state, prefer composables)
// 6. @/components/ui/...
// 7. @/lib/utils (cn)
// 8. lucide-vue-next icons
// 9. Types/interfaces (inline or imported)
</script>

<template>
  <!-- single root element -->
</template>
```

### Props
```typescript
// No defaults needed:
defineProps<{
  collapsed: boolean
  title: string
  items?: Item[]          // optional with ?
}>()

// With defaults:
const props = withDefaults(defineProps<{
  variant?: 'default' | 'outline'
  size?: 'sm' | 'default' | 'lg'
  class?: HTMLAttributes['class']   // always add if component accepts external class
}>(), {
  variant: 'default',
  size: 'default',
})
```

### Emits
```typescript
// No payload:
defineEmits<{
  toggle: []
  close: []
}>()

// With payload:
defineEmits<{
  select: [item: Item]
  update: [id: string, value: string]
}>()
```

### Class Merging (cn helper)
Always use `cn()` when a component accepts an external `class` prop:
```typescript
import { cn } from '@/lib/utils'
// In template:
:class="cn('base-classes here', props.class)"
```

### Icons
Always from `lucide-vue-next`. Control size with `:size="16"` (not CSS width/height).
Common sizes: 14 (inline text), 16 (buttons/inputs), 18 (headers), 20 (feature icons).

### UI Components available in `components/ui/`
| Import | Components |
|--------|-----------|
| `@/components/ui/button` | `Button`, `buttonVariants`, `ButtonVariants` |
| `@/components/ui/card` | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter` |

---

## Composable Rules

### Standard async composable template
```typescript
import { ref, readonly } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { fooApi, type FooItem } from '@/services/api'

export function useFoo() {
  const items = ref<FooItem[]>([])

  const { isLoading, error, execute: refresh } = useAsyncState(
    async () => {
      items.value = await fooApi.list()
    },
    undefined,
    { immediate: true },
  )

  async function createFoo(name: string) {
    const item = await fooApi.create({ name })
    items.value.push(item)       // optimistic local update, no re-fetch
    return item
  }

  async function deleteFoo(id: string) {
    await fooApi.delete(id)
    items.value = items.value.filter((i) => i.id !== id)
  }

  return {
    items: readonly(items),      // ALWAYS readonly
    isLoading,
    error,
    refresh,                     // renamed from execute
    createFoo,
    deleteFoo,
  }
}
```

### Rules
- Always wrap returned state with `readonly()`.
- Rename `execute` → `refresh` in the return value.
- Use `{ immediate: true }` so data loads on composable creation.
- Composables do NOT catch errors themselves — they throw, and Views handle with toast.
- Use optimistic local state updates (push/filter) instead of re-fetching.

### Pure computed composable (no async)
```typescript
export function useBreadcrumbs() {
  const route = useRoute()
  const breadcrumbs = computed<Breadcrumb[]>(() =>
    route.matched
      .filter((r) => r.meta?.breadcrumb)
      .map((r) => ({ name: r.meta.breadcrumb as string, path: r.path || '/' })),
  )
  return { breadcrumbs }
}
```

---

## Pinia Store Rules

Use **Setup Store** (never Options API):
```typescript
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', () => {
  // State — ref
  const count = ref(0)

  // Getters — computed
  const doubleCount = computed(() => count.value * 2)

  // Actions — plain functions
  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})
```

- Store ID: camelCase string matching the export variable name without `use` prefix and `Store` suffix.
- Prefer composables over stores for server data. Use stores for truly global cross-feature state.

---

## Service / API Rules

All API code lives in `src/services/api.ts`.

### Adding a new domain
```typescript
// ── FooDomain ─────────────────────────────────────────────────────────────
export interface FooItem {
  id: string
  name: string
  created_at: string
}

export interface CreateFooPayload {
  name: string
}

export const fooApi = {
  list: () =>
    apiClient.get<FooItem[]>('/foo/').then((r) => r.data),

  get: (id: string) =>
    apiClient.get<FooItem>(`/foo/${id}`).then((r) => r.data),

  create: (data: CreateFooPayload) =>
    apiClient.post<FooItem>('/foo/', data).then((r) => r.data),

  update: (id: string, data: Partial<CreateFooPayload>) =>
    apiClient.patch<FooItem>(`/foo/${id}`, data).then((r) => r.data),

  delete: (id: string) =>
    apiClient.delete(`/foo/${id}`).then((r) => r.data),
}
```

### Rules
- Every API method ends with `.then((r) => r.data)` — callers get business data, not axios Response.
- Interfaces are exported. Names: `FooItem` (entity), `CreateFooPayload` / `UpdateFooPayload` (payloads).
- Nested resources use path nesting: `/foo/:fooId/bars`.
- Separate domains with `// ── DomainName ───` comment dividers.

---

## View Rules

### Template layout structure
```vue
<template>
  <div class="space-y-6 max-w-4xl">

    <!-- Page header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground tracking-tight">Page Title</h1>
        <p class="text-sm text-muted-foreground mt-1">Description</p>
      </div>
      <!-- optional action button top-right -->
    </div>

    <!-- Error state (always first content block) -->
    <div v-if="error" class="flex items-center gap-2 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg px-4 py-3">
      <AlertCircle :size="16" class="shrink-0" />
      <span>{{ error instanceof Error ? error.message : String(error) }}</span>
    </div>

    <!-- Form / input card -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <div class="px-5 py-3 border-b border-border bg-muted/30">
        <h2 class="text-sm font-medium text-foreground">Section Title</h2>
      </div>
      <div class="p-4"><!-- form content --></div>
    </div>

    <!-- Data card: three-state (loading / empty / list) -->
    <div class="rounded-xl border border-border bg-card overflow-hidden">
      <!-- Loading -->
      <div v-if="isLoading" class="flex items-center justify-center gap-2 py-12 text-muted-foreground">
        <Loader2 :size="18" class="animate-spin" />
        <span class="text-sm">載入中…</span>
      </div>
      <!-- Empty -->
      <div v-else-if="items.length === 0" class="flex flex-col items-center gap-3 py-12 text-muted-foreground">
        <PackageOpen :size="32" class="opacity-40" />
        <span class="text-sm">尚無資料</span>
      </div>
      <!-- List -->
      <ul v-else class="divide-y divide-border">
        <li v-for="item in items" :key="item.id" class="flex items-center gap-3 px-5 py-3 hover:bg-muted/30 transition-colors">
          <!-- item content -->
        </li>
      </ul>
    </div>

  </div>
</template>
```

### Script setup pattern
```typescript
// Composable data + actions
const { items, isLoading, error, createFoo, deleteFoo, refresh } = useFoo()

// Local UI state
const newName = ref('')
const isCreating = ref(false)
const deletingId = ref<string | null>(null)

// Event handler: always try/catch + toast
async function handleCreate() {
  if (!newName.value.trim()) return
  isCreating.value = true
  try {
    await createFoo(newName.value.trim())
    toast.success('已建立', { description: `「${newName.value}」已新增。` })
    newName.value = ''
  } catch (err) {
    toast.error('建立失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
  } finally {
    isCreating.value = false
  }
}
```

### Toast messages (vue-sonner)
```typescript
import { toast } from 'vue-sonner'

toast.success('操作成功', { description: '說明文字' })
toast.error('操作失敗', { description: err instanceof Error ? err.message : '未知錯誤' })
```

---

## Router Rules

```typescript
// In router/index.ts, add inside the routes array:
{
  path: '/domain/resource',
  name: 'domain-resource',                              // kebab-case
  component: () => import('@/views/domain/ResourceView.vue'),  // lazy load
  meta: { breadcrumb: '頁面名稱' },                     // REQUIRED
},

// Group entry (no component):
{
  path: '/domain',
  redirect: '/domain/default-child',
  meta: { breadcrumb: '群組名稱' },
},

// Dynamic route:
{
  path: '/domain/resource/:id',
  name: 'domain-resource-detail',
  component: () => import('@/views/domain/ResourceDetailView.vue'),
  meta: { breadcrumb: '詳情' },
},
```

### Rules
- Every route **must** have `meta: { breadcrumb: '...' }`.
- Route `name` is always kebab-case.
- All components use `() => import(...)` lazy loading except the home route.
- All import paths use `@/views/...` alias.
