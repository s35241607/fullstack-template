import type { ColDef, GridOptions, ICellEditorParams } from 'ag-grid-community'

export type AgGridRowData = Record<string, unknown>
export type AgGridColumnDef = ColDef<AgGridRowData>
export type AgGridOptions = GridOptions<AgGridRowData>

export interface SearchableSelectEditorParams extends ICellEditorParams<AgGridRowData> {
  values?: string[]
}
