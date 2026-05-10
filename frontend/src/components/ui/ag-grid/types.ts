import type { ColDef, ColGroupDef, GridOptions, ICellEditorParams } from 'ag-grid-community'

export type AgGridRowData = Record<string, unknown>
export type AgGridColumnDef = ColDef<AgGridRowData> | ColGroupDef<AgGridRowData>
export type AgGridOptions = GridOptions<AgGridRowData>

export interface SearchableSelectEditorParams extends ICellEditorParams<AgGridRowData> {
  values?: string[]
}
