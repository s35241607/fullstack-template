<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

export interface SimpleTableColumn {
  key: string
  header: string
  align?: 'left' | 'center' | 'right'
  class?: string
}

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class']
    columns: SimpleTableColumn[]
    data: Record<string, unknown>[]
    rowKey?: string
    loading?: boolean
    emptyText?: string
  }>(),
  {
    rowKey: 'id',
    emptyText: '沒有資料',
  },
)

const emit = defineEmits<{
  'row-click': [row: Record<string, unknown>]
}>()
</script>

<template>
  <div :class="cn('rounded-md border', props.class)">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead
            v-for="col in columns"
            :key="col.key"
            :class="cn(
              col.align === 'center' && 'text-center',
              col.align === 'right' && 'text-right',
              col.class,
            )"
          >
            {{ col.header }}
          </TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        <!-- Loading -->
        <template v-if="loading">
          <TableRow v-for="i in 3" :key="`skeleton-${i}`">
            <TableCell v-for="col in columns" :key="col.key">
              <div class="h-4 animate-pulse rounded bg-muted" />
            </TableCell>
          </TableRow>
        </template>

        <!-- Empty -->
        <TableRow v-else-if="data.length === 0">
          <TableCell :colspan="columns.length" class="h-24 text-center text-muted-foreground">
            {{ emptyText }}
          </TableCell>
        </TableRow>

        <!-- Data -->
        <template v-else>
          <TableRow
            v-for="row in data"
            :key="String(row[rowKey])"
            class="cursor-pointer"
            @click="emit('row-click', row)"
          >
            <TableCell
              v-for="col in columns"
              :key="col.key"
              :class="cn(
                col.align === 'center' && 'text-center',
                col.align === 'right' && 'text-right tabular-nums',
                col.class,
              )"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                {{ row[col.key] }}
              </slot>
            </TableCell>
          </TableRow>
        </template>
      </TableBody>
    </Table>
  </div>
</template>
