# Frontend Code Review Checklist

Use this checklist when performing a code review (Mode B). Check every item and report results using the structured report format in SKILL.md.

---

## TypeScript

- [ ] No `any` types — use proper interfaces or `unknown`
- [ ] All function parameters and return types are typed (explicit or clearly inferred)
- [ ] Props use `defineProps<{}>()` generic syntax, not runtime validators
- [ ] Emits use `defineEmits<{ event: [payload?] }>()` generic syntax
- [ ] `withDefaults` used when props need default values
- [ ] No `@ts-ignore` or `@ts-expect-error` without explanation comment
- [ ] Imported types use `import type` to avoid runtime cost

## Vue Conventions

- [ ] `<script setup lang="ts">` (no Options API, no `export default`)
- [ ] Import order: vue → @vueuse → @/composables → @/services → @/stores → @/components → @/lib → lucide
- [ ] No direct DOM manipulation (`document.querySelector`, etc.) — use `ref` + template refs
- [ ] `v-for` always has `:key` with a stable unique ID (not array index unless list is static)
- [ ] `v-if` and `v-for` never on the same element (use `<template v-for>` wrapping `v-if`)
- [ ] Components in `components/ui/` accept and merge external `class` prop via `cn()`

## Composables

- [ ] Returned state is wrapped in `readonly()`
- [ ] `execute` from `useAsyncState` is renamed to `refresh` in return value
- [ ] `useAsyncState` uses `{ immediate: true }` for auto-loading data
- [ ] Composable does NOT toast errors internally — it throws, Views handle
- [ ] No direct `axiosClient` calls in composables — goes through `services/api.ts`

## Pinia Stores

- [ ] Uses Setup Store `defineStore('id', () => { ... })`, not Options API
- [ ] Only used for truly global state; server data lives in composables
- [ ] State uses `ref`, getters use `computed`, actions use plain functions

## API Service

- [ ] All methods inside domain API objects (e.g., `fooApi = { ... }`)
- [ ] Every method ends with `.then((r) => r.data)`
- [ ] TypeScript interfaces exported for all entity types and payloads
- [ ] Domain sections separated by `// ── DomainName ───` dividers
- [ ] No hardcoded base URLs — uses `apiClient` from the top of the file

## Views

- [ ] Outer wrapper: `<div class="space-y-6 max-w-4xl">`
- [ ] Error state rendered with `v-if="error"` at top of content
- [ ] Data list/table has three-state pattern: `isLoading` → empty check → actual content
- [ ] Every user action (create/delete/update) wrapped in `try/catch` with toast feedback
- [ ] `isCreating` / `isDeleting` / `isSaving` local refs used to prevent double-submit and show loading state
- [ ] Inputs cleared after successful create
- [ ] No raw `console.log` in production code

## Router

- [ ] Every route has `meta: { breadcrumb: '...' }`
- [ ] Route `name` is kebab-case
- [ ] All routes (except home) use `() => import(...)` lazy loading
- [ ] All import paths use `@/views/...` alias

## Accessibility & UX

- [ ] Interactive elements are `<button>` or `<a>`, not `<div onClick>`
- [ ] `<button>` elements have descriptive text or `aria-label`
- [ ] Loading states show visual feedback (spinner + text)
- [ ] Destructive actions (delete) show confirmation or have obvious visual affordance
- [ ] Form inputs have associated labels or `aria-label`

## Tailwind CSS

- [ ] No inline `style=""` for values achievable with Tailwind
- [ ] No magic numbers in className strings — use Tailwind scale values
- [ ] `cn()` used for conditional class merging (not template literals with ternaries)
- [ ] Dark mode uses `text-foreground`, `bg-background`, `border-border` CSS variables (not hardcoded colors)
- [ ] No `!important` modifier unless absolutely necessary (document with comment)
