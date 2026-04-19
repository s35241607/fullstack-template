import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

export interface Breadcrumb {
  name: string
  path: string
}

function resolvePath(pattern: string, params: Record<string, string | string[]>): string {
  return pattern.replace(/:(\w+)/g, (_, key) => {
    const val = params[key]
    return Array.isArray(val) ? val[0] : (val ?? '')
  })
}

function formatParamLabel(paramName: string, paramValue: string): string {
  if (paramName === 'orderId') {
    return paramValue.replace(/^po-/, 'PO-').toUpperCase()
  }
  if (paramName === 'lineId') {
    const match = paramValue.match(/line-(\d+)$/)
    return match ? match[1] : paramValue
  }
  return paramValue
}

export function useBreadcrumbs() {
  const route = useRoute()
  const { t } = useI18n()

  const breadcrumbs = computed<Breadcrumb[]>(() => {
    if (route.path === '/') return []

    return route.matched
      .filter((r) => r.meta?.breadcrumb || r.meta?.breadcrumbParam)
      .map((r) => {
        const resolvedPath = resolvePath(r.path, route.params)

        if (r.meta.breadcrumb) {
          return {
            name: t(r.meta.breadcrumb as string),
            path: resolvedPath || '/',
          }
        }

        const paramName = r.meta.breadcrumbParam as string
        const paramValue = route.params[paramName] as string
        const prefix = r.meta.breadcrumbPrefix
          ? t(r.meta.breadcrumbPrefix as string) + ' '
          : ''
        return {
          name: prefix + formatParamLabel(paramName, paramValue),
          path: resolvedPath,
        }
      })
  })

  return { breadcrumbs }
}

