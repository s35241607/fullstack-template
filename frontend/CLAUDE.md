# Frontend Development Guidelines (Vue 3 + shadcn-vue)

## Component Rules
- **Atomic UI**: `src/components/ui/` (controlled via shadcn-vue CLI). No business logic.
- **Layout/Business**: `src/components/layout/`. Compose using `ui/` atoms.
- **Styles**: Modify CVA in `ui/` components for reused styles. Use Tailwind inline classes only for one-off layouts.
- **Composition API**: Use `<script setup lang="ts">`.
- **Props/Emits**: Properly type and document. Use `v-bind="$attrs"` for wrappers.

## Tooling & Deps
- **Icons**: `lucide-vue-next`.
- **Toasts**: `vue-sonner` (global `<Toaster>` in `App.vue`).
- **UI Base**: `reka-ui` (formerly radix-vue).
- **Styles**: `cn()` utility in `src/lib/utils.ts` for mergers.

## Data & State
- **Composables**: Return `readonly` state. Use `useAsyncState` with `{ immediate: true }`.
- **Stores**: Setup Store (Pinia). Prefer composables for local state.
- **API**: Centralized in `src/services/api.ts`. Method must `.then((r) => r.data)`.

## I18N
- 100% user-visible text must use `$t()`.
- Add keys to `en.ts` (base) -> `zh-TW.ts` (translation).
- Key Format: `section.feature.label`.

## Fonts
- Family: `'Inter Variable', 'Noto Sans TC', sans-serif`.
- Loaded via `@fontsource` in `main.ts`. No Google Fonts CDN.

## Development Checklist
- [ ] Use `pnpm dlx shadcn-vue@latest add [name]` for new UI components.
- [ ] Ensure all text is in i18n locales.
- [ ] Check if reused styles can be moved to CVA variant.
- [ ] Implement `v-bind="$attrs"` for wrapper components.
