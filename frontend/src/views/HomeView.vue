<script setup lang="ts">
  import { FileText, Zap } from 'lucide-vue-next'

  const apiDocsUrl = import.meta.env.VITE_API_DOCS_URL || '/docs'

  const modules = [
    {
      key: 'api',
      icon: Zap,
      path: apiDocsUrl,
      external: true,
      accent: 'bg-teal-500/10 text-teal-600 dark:text-teal-400',
    },
  ]
</script>

<template>
  <div class="space-y-8 max-w-5xl">
    <!-- Hero -->
    <div class="rounded-xl border border-border bg-card p-6 sm:p-8 text-center sm:text-left">
      <div class="flex flex-col sm:flex-row sm:items-center gap-6">
        <div
          class="flex items-center justify-center w-16 h-16 rounded-2xl bg-primary text-primary-foreground text-3xl font-bold shrink-0 mx-auto sm:mx-0"
        >
          <FileText :size="32" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-foreground tracking-tight">
            {{ $t('home.title') }}
          </h1>
          <p class="text-muted-foreground mt-2 text-lg">
            {{ $t('home.subtitle') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Quick Start -->
    <div>
      <h2 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
        Quick Start
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <component
          :is="m.external ? 'a' : 'RouterLink'"
          v-for="m in modules"
          :key="m.key"
          v-bind="m.external ? { href: m.path, target: '_blank', rel: 'noopener' } : { to: m.path }"
          class="group flex flex-col gap-4 rounded-xl border border-border bg-card p-6 hover:border-primary/30 hover:shadow-md transition-all duration-300"
        >
          <div
            class="flex items-center justify-center w-12 h-12 rounded-lg transition-colors"
            :class="m.accent"
          >
            <component :is="m.icon" :size="24" />
          </div>
          <div>
            <p
              class="font-semibold text-foreground text-lg group-hover:text-primary transition-colors"
            >
              {{ $t(`home.moduleCards.${m.key}.title`) }}
            </p>
            <p class="text-sm text-muted-foreground mt-1 leading-relaxed">
              {{ $t(`home.moduleCards.${m.key}.desc`) }}
            </p>
          </div>
        </component>
      </div>
    </div>
  </div>
</template>
