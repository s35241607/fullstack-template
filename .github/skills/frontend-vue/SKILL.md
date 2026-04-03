---
name: frontend-vue
description: >
  Frontend development skill for this project's Vue 3 + TypeScript + Tailwind CSS v4 + shadcn-vue stack.
  USE THIS SKILL whenever the user wants to:
  (A) generate a new Vue component,
  (B) review existing frontend code for convention/quality issues,
  (C) scaffold a full page feature (View + composable + API + router).
  Trigger on: "新增元件", "建立頁面", "審查前端", "新功能", "add view", "create component", "review UI", "refactor composable", "add API", "add route".
---

This skill enforces the exact conventions used throughout this project's frontend codebase. Always follow these patterns precisely — no exceptions — since Copilot-generated code that deviates from them causes inconsistency and review churn.

Read `references/conventions.md` for the full code convention reference before generating any code. Read `references/review-checklist.md` when performing a review task.

---

## Task Detection

Identify which mode applies from the user's request:

| Mode                          | Trigger keywords                                            | Action                                                    |
| ----------------------------- | ----------------------------------------------------------- | --------------------------------------------------------- |
| **A — Generate Component**    | "建立元件", "新增元件", "create component", "add component" | Follow [Component Generation](#a--component-generation)   |
| **B — Review Code**           | "審查", "review", "check", "audit", "問題"                  | Follow [Code Review](#b--code-review)                     |
| **C — Scaffold Full Feature** | "建立頁面", "新功能", "add view", "new feature", "add page" | Follow [Full Feature Scaffold](#c--full-feature-scaffold) |

If the request is ambiguous, ask once: "你想要 (A) 產生元件、(B) 審查程式碼，或是 (C) 建立完整頁面功能？"

---

## A — Component Generation

Generate a single `.vue` file that follows project conventions exactly.

**Steps:**

1. Clarify if missing: component location (`components/ui/` vs `components/layout/` vs `components/`), props, emits, behaviour.
2. Read `references/conventions.md` section "Component Rules" before writing.
3. Output the complete file. Never output partial snippets for a new component.

**Required file header pattern:**

```vue
<script setup lang="ts">
// imports first: vue, then @vueuse, then @/composables, then @/lib, then lucide
</script>

<template>
  <!-- root element always has a semantic role or descriptive comment -->
</template>
```

**Placement rules:**

- Generic reusable UI → `src/components/ui/<name>/` (with `index.ts` barrel + `cva` variants if it accepts variants)
- Layout shell elements → `src/components/layout/`
- Feature-specific, non-reusable → `src/components/`

---

## B — Code Review

Perform a structured review. Read `references/review-checklist.md` for the full checklist, then produce a report in this format:

```
## Code Review: <filename>

### ✅ Passes
- ...

### ⚠️ Warnings (should fix)
- ...

### ❌ Errors (must fix)
- ...

### 💡 Suggestions (optional improvements)
- ...
```

Always include concrete fix examples for every ⚠️ and ❌ item.

---

## C — Full Feature Scaffold

Scaffold all layers for a new feature. Work in this order to avoid forward-reference issues:

```
1. services/api.ts         — add TypeScript interface + API object
2. composables/use<Name>.ts — create composable using useAsyncState
3. views/<domain>/<Name>View.vue — create View
4. router/index.ts         — register lazy route with meta.breadcrumb
```

**For each layer**, read the corresponding section in `references/conventions.md` before writing.

**Checklist before finishing:**

- [ ] Interface exported from `api.ts`
- [ ] Composable returns `readonly(data)`, `isLoading`, `error`, `refresh` + action fns
- [ ] View uses `try/catch` + `vue-sonner` toast for all user actions
- [ ] View template has loading / empty / list three-state pattern
- [ ] Route has `meta: { breadcrumb: '...' }` and kebab-case `name`
- [ ] All imports use `@/` alias
