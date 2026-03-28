import { computed } from 'vue'
import { useRoute } from 'vue-router'

export interface Breadcrumb {
  name: string
  path: string
}

export function useBreadcrumbs() {
  const route = useRoute()

  const breadcrumbs = computed<Breadcrumb[]>(() => {
    const crumbs = route.matched
      .filter((r) => r.meta?.breadcrumb)
      .map((r) => ({
        name: r.meta.breadcrumb as string,
        path: r.path || '/',
      }))

    // On home page, show nothing extra (just the Home icon in the header)
    if (route.path === '/') return []

    return crumbs
  })

  return { breadcrumbs }
}
