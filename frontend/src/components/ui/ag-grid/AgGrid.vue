<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  TextFilterModule,
  NumberFilterModule,
  DateFilterModule,
  ValidationModule,
  TextEditorModule,
  NumberEditorModule,
  DateEditorModule,
  CheckboxEditorModule,
  SelectEditorModule,
  UndoRedoEditModule,
  CellStyleModule,
  RowSelectionModule,
  ColumnAutoSizeModule,
  themeQuartz,
  type Theme,
} from 'ag-grid-community'
import { computed, ref } from 'vue'
import { useDark } from '@vueuse/core'

// Register all required community modules
ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  TextFilterModule,
  NumberFilterModule,
  DateFilterModule,
  ValidationModule,
  TextEditorModule,
  NumberEditorModule,
  DateEditorModule,
  CheckboxEditorModule,
  SelectEditorModule,
  UndoRedoEditModule,
  CellStyleModule,
  RowSelectionModule,
  ColumnAutoSizeModule,
])

interface Props {
  rowData: any[]
  columnDefs: any[]
  height?: string | number
  gridOptions?: any
}

const props = withDefaults(defineProps<Props>(), {
  height: '500px',
  gridOptions: () => ({})
})

const isDark = useDark()

/**
 * AG Grid v35 Theming API (official approach):
 * 
 * themeQuartz uses `colorSchemeVariable` by default.
 * It reacts to `data-ag-theme-mode` attribute on any parent element.
 * We set this attribute on the wrapper div and toggle it reactively.
 * 
 * Ref: https://www.ag-grid.com/vue-data-grid/theming-colors/#theme-modes
 */
const gridTheme = computed<Theme>(() => {
  return themeQuartz.withParams({
    borderRadius: 6,
    headerHeight: 38,
    rowHeight: 36,
    fontSize: 14,
    fontFamily: 'inherit', // Follows the parent application font
    backgroundColor: isDark.value ? '#09090b' : '#ffffff',
    foregroundColor: isDark.value ? '#fafafa' : '#09090b',
    headerBackgroundColor: isDark.value ? '#09090b' : '#f9fafb',
    headerTextColor: isDark.value ? '#a1a1aa' : '#71717a',
    borderColor: isDark.value ? '#27272a' : '#e4e4e7',
    headerColumnSeparatorColor: 'transparent',
  })
})

const themeMode = computed(() => isDark.value ? 'dark' : 'light')

const gridApi = ref()

const onGridReady = (params: any) => {
  gridApi.value = params.api
}

const defaultColDef = {
  flex: 1,
  minWidth: 100,
  resizable: true,
  sortable: true,
  filter: true,
  editable: true,
  suppressMovable: false,
}

// Handle custom key behavior if needed
const onCellKeyDown = (params: any) => {
  // We let AG Grid's built-in logic handle Enter and Escape 
  // to avoid conflicting with the editor's lifecycle.
}

// Function to copy selected data to clipboard
const copySelected = () => {
  if (!gridApi.value) return
  const selectedRows = gridApi.value.getSelectedRows()
  if (selectedRows.length === 0) return
  
  const text = selectedRows.map((row: any) => 
    Object.values(row).join('\t')
  ).join('\n')
  
  navigator.clipboard.writeText(text)
}

defineExpose({
  gridApi,
  copySelected
})
</script>

<template>
  <!--
    The key to dark mode: set data-ag-theme-mode on a parent element.
    themeQuartz uses colorSchemeVariable by default, which reads this attribute.
  -->
  <div 
    :data-ag-theme-mode="themeMode"
    class="w-full overflow-hidden border rounded-xl shadow-sm transition-colors duration-300"
    :class="isDark ? 'border-slate-700/50' : 'border-slate-200'"
    :style="{ height: typeof height === 'number' ? height + 'px' : height }"
  >
    <AgGridVue
      class="w-full h-full"
      :theme="gridTheme"
      :rowData="rowData"
      :columnDefs="columnDefs"
      :defaultColDef="defaultColDef"
      :animateRows="true"
      :rowSelection="'multiple'"
      :enableCellTextSelection="true"
      :ensureDomOrder="true"
      @grid-ready="onGridReady"
      @cell-key-down="onCellKeyDown"
      v-bind="gridOptions"
    />
  </div>
</template>

<style>
/* --- Notion-like Global Adjustments --- */
.ag-theme-quartz, .ag-theme-quartz-dark {
  --ag-border-radius: 6px;
  --ag-grid-size: 6px;
  --ag-list-item-height: 32px;
}

/* Custom Selection Border (Primary Color) */
.ag-cell-focus:not(.ag-cell-editing) {
  border: 2px solid hsl(var(--primary)) !important;
  outline: none !important;
}

/* Hide default editor border to avoid double border */
.ag-cell-editing {
  border: 2px solid hsl(var(--primary)) !important;
  padding: 0 !important;
}

/* Fill Handle square */
.ag-cell-focus:not(.ag-cell-editing)::after {
  content: "";
  position: absolute;
  right: -4px;
  bottom: -4px;
  width: 7px;
  height: 7px;
  background-color: hsl(var(--primary));
  border: 1px solid white;
  z-index: 10;
  cursor: crosshair;
}

/* Remove horizontal lines between header cells for a cleaner look */
.ag-header-cell::after {
  display: none !important;
}

/* Header Text Style */
.ag-header-cell-label {
  font-weight: 500 !important;
  text-transform: none;
  letter-spacing: normal;
}

/* Selected row highlight */
.ag-row-selected {
  background-color: color-mix(in srgb, var(--ag-accent-color, #2563eb) 8%, var(--ag-background-color, #fff)) !important;
}
</style>
