<script setup lang="ts">
import { Package, Zap, Database, Globe } from 'lucide-vue-next'

const techStack = [
  { label: 'Vue 3', desc: 'Composition API', color: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' },
  { label: 'TypeScript', desc: 'Type safety', color: 'bg-blue-500/10 text-blue-600 dark:text-blue-400' },
  { label: 'Tailwind CSS 4', desc: 'Utility-first', color: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400' },
  { label: 'Vite 8', desc: 'Fast builds', color: 'bg-purple-500/10 text-purple-600 dark:text-purple-400' },
  { label: 'FastAPI', desc: 'Python backend', color: 'bg-teal-500/10 text-teal-600 dark:text-teal-400' },
  { label: 'SQLAlchemy', desc: 'ORM + Alembic', color: 'bg-orange-500/10 text-orange-600 dark:text-orange-400' },
  { label: 'PostgreSQL 16', desc: 'via Docker Compose', color: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400' },
  { label: 'Pinia', desc: 'State management', color: 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400' },
  { label: 'Radix Vue', desc: 'Accessible UI', color: 'bg-pink-500/10 text-pink-600 dark:text-pink-400' },
]

const cards = [
  {
    title: 'Items',
    desc: 'Full CRUD via FastAPI backend with PostgreSQL 16',
    icon: Package,
    path: '/items',
    accent: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  },
  {
    title: 'Fast API',
    desc: 'RESTful endpoints, auto-docs at /docs',
    icon: Zap,
    path: 'http://localhost:8000/docs',
    external: true,
    accent: 'bg-teal-500/10 text-teal-600 dark:text-teal-400',
  },
  {
    title: 'PostgreSQL 16',
    desc: 'Async SQLAlchemy with Clean Architecture',
    icon: Database,
    path: '/items',
    accent: 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
  },
  {
    title: 'Vite Proxy',
    desc: '/api/* proxied to backend automatically',
    icon: Globe,
    path: '/about',
    accent: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
  },
]
</script>

<template>
  <div class="space-y-8 max-w-4xl">
    <!-- Hero -->
    <div class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground text-xl font-bold shrink-0">
          M
        </div>
        <div>
          <h1 class="text-2xl font-bold text-foreground tracking-tight">
            Welcome to MyApp
          </h1>
          <p class="text-muted-foreground mt-1">
            A fullstack template built with Vue 3 + FastAPI — ready to go.
          </p>
        </div>
      </div>
    </div>

    <!-- Quick nav cards -->
    <div>
      <h2 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
        Quick access
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <component
          :is="card.external ? 'a' : 'RouterLink'"
          v-for="card in cards"
          :key="card.title"
          v-bind="card.external ? { href: card.path, target: '_blank', rel: 'noopener' } : { to: card.path }"
          class="group flex flex-col gap-3 rounded-lg border border-border bg-card p-4 hover:border-primary/30 hover:shadow-sm transition-all"
        >
          <div
            class="flex items-center justify-center w-9 h-9 rounded-md transition-colors"
            :class="card.accent"
          >
            <component :is="card.icon" :size="18" />
          </div>
          <div>
            <p class="font-medium text-foreground text-sm group-hover:text-primary transition-colors">
              {{ card.title }}
            </p>
            <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
              {{ card.desc }}
            </p>
          </div>
        </component>
      </div>
    </div>

    <!-- Tech stack -->
    <div>
      <h2 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
        Tech stack
      </h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div
          v-for="tech in techStack"
          :key="tech.label"
          class="rounded-lg border border-border bg-card px-3 py-2.5"
        >
          <p
            class="text-xs font-semibold"
            :class="tech.color"
          >
            {{ tech.label }}
          </p>
          <p class="text-xs text-muted-foreground mt-0.5">{{ tech.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
