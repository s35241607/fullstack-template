# AG Grid 客製化封裝元件

基於 **AG Grid Community v35**（`ag-grid-vue3`）的 Vue 3 封裝，在原生功能之上疊加了一套完整的 Excel 風格互動體驗。

## 元件清單

| 檔案 | 說明 |
|------|------|
| `AgGrid.vue` | 主要封裝元件，包含所有 Excel 風格功能 |
| `SearchableSelectEditor.vue` | 可搜尋下拉選單 Cell Editor（popup 彈出式） |
| `types.ts` | 封裝對外使用的 row / column / editor 型別 |
| `index.ts` | 統一匯出入口 |
| `UT.md` | Excel 功能驗證清單 (測試用例) |

---

## 可復用方式

這個資料表已經可以作為獨立元件搬到其他專案使用。外部專案主要替換三件事：

- `rowData`：任意列資料陣列
- `columnDefs`：AG Grid Community 的欄位設定，可為每個欄位指定 editor、formatter、renderer
- `gridOptions`：不同專案需要的排序、過濾、context、事件等 AG Grid 選項

```ts
import {
  AgGrid,
  SearchableSelectEditor,
  type AgGridColumnDef,
  type AgGridRowData,
} from '@/components/ui/ag-grid'

const rowData: AgGridRowData[] = [
  { name: 'MacBook Pro', status: '有庫存' },
]

const columnDefs: AgGridColumnDef[] = [
  { field: 'name', headerName: '產品名稱' },
  {
    field: 'status',
    headerName: '狀態',
    cellEditor: SearchableSelectEditor,
    cellEditorPopup: true,
    cellEditorParams: {
      values: ['有庫存', '低庫存', '缺貨'],
    },
  },
]
```

```vue
<AgGrid :row-data="rowData" :column-defs="columnDefs" height="500px" />
```

若不同專案有不同下拉清單，只需要在各欄位的 `cellEditorParams.values` 傳入該專案自己的選項。

### API-driven Demo

`/ag-grid-api-demo` 展示建議的 API 整合方式：

- `AgGrid.vue` 保持純 UI/互動封裝，只接收 `rowData`、`columnDefs`、`gridOptions`
- 頁面層負責呼叫資料 API，並把分頁、排序、篩選條件轉成 query payload
- 下拉清單由 lookup API 取得，再注入外部篩選器與 `SearchableSelectEditor` 的 `cellEditorParams.values`

Mock API 位於 `src/services/agGridMockApi.ts`，可作為日後串真實後端時的 payload 參考。

---

## 客製化功能詳解

### 1. Excel 風格多格範圍選取

AG Grid Community 版本不含原生範圍選取（Enterprise 功能），本元件完整手動實作。

**操作方式：**
- **滑鼠拖曳**：按住左鍵拖曳選取矩形範圍
- **Shift + 點擊**：擴展現有選取範圍的終點
- **Ctrl/Cmd + 點擊**：新增獨立選取範圍（不連續多選）
- **Shift + 方向鍵**：以鍵盤擴展選取範圍

**實作細節：**
- `selectedRanges`：`CellRange[]`，每個 range 由 `start`/`end` CellPoint 組成
- `cellClassRules` 透過 `isCellSelected()` 判斷選取狀態並套用 `custom-range-selected` 樣式
- `onCellFocused` 事件監聽 AG Grid 原生 focus 移動（方向鍵），同步更新 `selectedRanges`
- `_suppressFocusSync` flag（非 reactive）防止滑鼠選取與程式呼叫 `setFocusedCell` 時觸發迴圈

**視覺呈現：**
- 單格選取：沿用 `.ag-cell-focus` CSS border（primary 色）
- 多格範圍：`selection-range-overlay` div（藍色外框）覆蓋在 grid 之上
- 選取範圍背景：`custom-range-selected` class 使用 `hsl(var(--primary))` 淡色混合，跟隨主題色

---

### 2. 自訂剪貼簿（Ctrl+C / Ctrl+V）

完全繞過 AG Grid 內建剪貼簿，用 `@keydown.capture` 在捕獲階段攔截，確保 AG Grid 無法在 bubble 階段先行消化事件。

**複製（Ctrl+C）：**
- 將所有選取範圍展平成 TSV（Tab-Separated Values）字串
- 多個 range 的資料依 range 順序合併，每列一行
- 呼叫 `navigator.clipboard.writeText()` 寫入系統剪貼簿
- 儲存 `copyRanges` 以顯示「螞蟻行軍」動畫框

**貼上（Ctrl+V）：**
- 從 `navigator.clipboard.readText()` 讀取文字
- 解析 TSV 為二維矩陣 `ClipboardMatrix = string[][]`
- **智慧重複填充**：若選取範圍大小是來源矩陣的整數倍，自動鋪磚重複填充（如 Excel）
- **跳過不可編輯格**：尊重 `editable`、`suppressPaste` 等 colDef 設定
- **型別解析**：`parsePastedValue()` 依 `cellDataType` 或現有值型別自動轉換 number / boolean

**安全性：**
- `isClipboardEventFromEditor()` 判斷事件是否來自 input/textarea/editor，若是則不攔截，讓 editor 自己處理複製貼上

---

### 3. 填充柄（Fill Handle）

仿 Excel 右下角小方塊，拖曳可快速填充資料。

**操作方式：**
- 將滑鼠移到選取範圍右下角的藍色小方塊
- 按住左鍵拖曳到目標範圍

**實作細節：**
- `updateFillHandlePosition()`：查詢 `[row-index][col-id]` DOM 元素取得實際像素位置，相對 gridContainer 定位
- `computeFillExtendedRange()`：依拖曳方向（垂直 vs 水平距離較大者）決定延伸軸
- `applyFill()`：以來源範圍資料鋪磚填充，支援多欄、多列來源（鋪磚模式）
- 填充完成後 undo stack 記錄舊值，支援 Ctrl+Z 還原

**視覺：**
- 填充預覽：拖曳時顯示 `fill-preview` 虛線框
- 填充完成後選取範圍自動擴展為完整填充區域

---

### 4. 螞蟻行軍（Marching Ants）

複製後在原始範圍周圍顯示動態虛線框，與 Excel 行為一致。

- 按任意鍵（貼上、Esc 等）後自動消除
- 動畫：`copyRangePulse` keyframe，0.75s 來回閃爍

---

### 5. 自訂 Undo 堆疊（Ctrl+Z）

AG Grid 的 `UndoRedoEditModule` 只追蹤單格手動編輯，無法覆蓋本元件的批次貼上與填充操作，因此自行實作。

**機制：**
- `undoStack: UndoEntry[][]`：每次貼上/填充前記錄所有受影響格子的舊值
- 最大深度：100 步（`MAX_UNDO_STEPS`）
- Ctrl+Z 時：若有進行中的編輯先取消（`stopEditing(false)`），再套用 undo
- `setDataValue()` 配合 `'undo'` source，可在需要時識別來源

---

### 6. 暗黑模式

使用 AG Grid v35 官方 Theming API（`themeQuartz`），自動跟隨應用程式的暗黑模式切換。

**實作：**
- `useDark()`（VueUse）偵測系統/應用主題
- `gridTheme` computed 依 `isDark` 動態產生 `themeQuartz.withParams({...})`
- `data-ag-theme-mode` attribute 設在外層 wrapper div，驅動 AG Grid 顏色模式
- 所有顏色使用 CSS 變數（`hsl(var(--primary))` 等），與 shadcn-vue 設計 token 整合

---

### 7. Enter 鍵行為

| 狀態 | Enter 行為 |
|------|-----------|
| 一般格（非編輯模式） | 進入編輯模式（`startEditingCell`） |
| 編輯中（text/number editor） | 讓 editor 自己處理（提交值並結束） |
| Popup editor（SearchableSelectEditor） | editor 內部處理 Enter（選取高亮選項） |

在捕獲階段（`@keydown.capture`）判斷 `isClipboardEventFromEditor()`，若在 editor 內直接 return，不干涉。

---

### 8. SearchableSelectEditor（可搜尋下拉選單）

完全手動實作的 popup cell editor，使用 shadcn-vue 設計 token，不依賴 reka-ui 內部事件系統（避免與 AG Grid popup 生命週期衝突）。

**使用方式：**
```ts
import SearchableSelectEditor from '@/components/ui/ag-grid/SearchableSelectEditor.vue'

const colDefs = [
  {
    field: 'status',
    cellEditor: SearchableSelectEditor,
    cellEditorPopup: true,          // 必須設為 true
    cellEditorParams: {
      values: ['有庫存', '低庫存', '缺貨'],
    },
  },
]
```

**功能：**
- 搜尋框即時過濾選項
- 方向鍵上下移動高亮
- Enter 確認選取，Escape 取消，Tab 確認並移至下一格
- 滑鼠點擊選取（`@mousedown.prevent` 防止 input blur）
- 已選取項目顯示勾選圖示

**為何不用 shadcn `Command` 元件：**
reka-ui 的 `ListboxRoot`（`Command` 內部）有自己的 auto-focus 行為，與 AG Grid popup editor 的 `afterGuiAttached()` 生命週期衝突，且 `@select` 事件在 popup 容器中傳遞不穩定。

---

## 程式碼優化建議

> 以下列出曾有的優化需求，已完成的項目以 ✅ 標記。

### 已完成

#### ✅ 1. `refreshCells({ force: true })` 效能問題
`onCellMouseOver` 已改用 `requestAnimationFrame` 節流，拖曳選取時不再每格觸發完整重繪。

#### ✅ 2. `_suppressFocusSync` 的競態條件
`focusCell()` 已改為 `async` 函式，在 `setFocusedCell` 後 `await nextTick()` 再清除 flag，確保 `onCellFocused` 在 guard 生效期間執行。

#### ✅ 3. `ModuleRegistry.registerModules` 在模組層級執行
建議移到 `main.ts`（低優先，AG Grid 內部有去重保護）。

#### ✅ 4. `onBodyScroll` 重複觸發
`onBodyScroll` 已加入 `requestAnimationFrame` 節流，防止滾動時 layout thrashing。`onBodyViewportScroll` 已委派給 `onBodyScroll`。

#### ✅ 5. `gridOptions` prop 型別過於寬鬆
已改為 `GridOptions<GridRowData>`，提供完整型別檢查與 autocomplete。

#### ✅ 6. CSS 顏色硬編碼
所有 `rgba(37, 99, 235, ...)` 已改為 `color-mix(in srgb, hsl(var(--primary)) X%, transparent)`，換主題時自動跟隨。

#### ✅ 7. `computeRangeRect` 每次都查 DOM
已透過 `requestAnimationFrame` 批次更新策略緩解（`updateAllRects`）。

---

## 後續功能待辦

### 核心功能

- [x] **Redo（Ctrl+Y / Ctrl+Shift+Z）**：已實作（修復了原先早期返回條件錯誤導致 Ctrl+Shift+Z 失效的 bug）
- [x] **Delete / Backspace 清空選取範圍**：單格進入編輯模式，多格批次清空（含 undo）
- [ ] **Ctrl+D 向下填充**：複製最上方格子的值到選取範圍，仿 Excel 行為
- [ ] **右鍵選單（Context Menu）**：複製、貼上、刪除列、填充等常用操作

### 編輯器擴充

- [ ] **日期選擇器 Editor**（DatePickerEditor）：popup 行事曆 UI
- [ ] **多選標籤 Editor**（MultiSelectEditor）：允許一格存放多個 tag 值
- [ ] **數字輸入 Editor**：含上下箭頭微調、格式化顯示

### 資料管理

- [ ] **新增列**：快捷鍵（如 Alt+Insert）或底部按鈕新增空白列
- [ ] **刪除列**：選取整列後 Delete 鍵刪除（含 undo）
- [ ] **列拖曳排序**：拖曳列標頭重新排序，更新底層 rowData
- [ ] **欄位可見性控制**：側邊欄或 popover 切換欄位顯示/隱藏

### 匯入匯出

- [ ] **匯出 CSV**：將目前可見資料（含篩選結果）匯出為 CSV
- [ ] **匯出 Excel（.xlsx）**：使用 SheetJS（xlsx）套件
- [ ] **匯入 CSV/Excel**：拖曳或點擊上傳，解析後填入 rowData

### 狀態持久化

- [ ] **欄位寬度/排序/篩選狀態儲存**：呼叫 `api.getColumnState()` 存至 localStorage，下次載入還原
- [ ] **分頁（Pagination）**：大資料集的分頁顯示模式

### 進階顯示

- [ ] **欄位凍結（Column Pinning）**：固定前 N 欄不隨水平捲動
- [ ] **行列群組（Row Grouping / Aggregation）**：Enterprise 或自行實作
- [ ] **儲存格 Tooltip**：文字截斷時 hover 顯示完整內容
- [ ] **行內驗證**：欄位值不合規時顯示紅框與 tooltip 錯誤訊息
- [ ] **載入狀態骨架屏**：`rowData` 為 `null` 時顯示 skeleton rows

---

## 已修復問題 (Fixed Issues)

在驗證過程中發現並已修復的項目：

- [x] **Shift+Click 範圍選取失效**：修復了 `onCellFocused` 在 `mouseup` 後過早觸發導致選取範圍被重置為單格的問題。現在使用 `nextTick` 確保選取狀態穩定。
- [x] **JS Runtime Error (Undefined 'api')**：修復了 `handleMouseUp` 與 `onCellMouseDown` 中 `api` 變數未定義的錯誤，全面改用 `gridApi.value` 或 `params.api`。
- [x] **清理選取函式缺失**：修復了 `clearSelections` 呼叫了不存在的 `updateRangeSelection` 的問題，已改為正確的重繪邏輯。
- [x] **Redo 快捷鍵支援**：確認並修復了 `Ctrl+Y` 與 `Ctrl+Shift+Z` 的觸發邏輯。
- [x] **雙擊無法進入編輯模式**：由於 `onCellMouseDown` 觸發 `refreshCells` 會重建 DOM 導致雙擊失效。已優化邏輯，若點擊已聚焦格子則延遲或跳過重繪以保留雙擊事件。
- [x] **框選框遮擋凍結欄位**：將 Overlay 透過 `Teleport` 移入 AG Grid 內部的 `.ag-root` 容器，使其遵循原生的層級順序，滾動時會被凍結欄位正確遮擋。
- [x] **大量資料複製效能**：優化了 TSV 字串構建邏輯，使用預配置陣列提高大量儲存格複製時的反應速度。
- [x] **部分欄位無法複製 (valueGetter/格式化問題)**：全面改用 `api.getCellValue({ rowNode, colKey })` 獲取原始值，並手動安全調用 `colDef.valueFormatter` 函式來產生最終複製文字。
- [x] **Ctrl+Shift+Z Redo 永遠失效**：`onKeyDownCapture` 早期返回條件錯誤地包含了 `event.shiftKey`，導致 Ctrl+Shift+Z 在進入 `key === 'z'` 分支前就被過濾掉。已修復條件邏輯，僅過濾 `event.altKey`。
- [x] **ResizeObserver 記憶體洩漏**：`onGridReady` 中建立的 `ResizeObserver` 從未在 `onUnmounted` 中呼叫 `disconnect()`，已修復。
- [x] **`isSelecting` 競態條件**：`handleMouseUp` 同步清除 `isSelecting` 導致 `onCellFocused` 在多格選取結束後立刻重置範圍。改用 `nextTick` 延遲清除，確保 guard 在事件觸發期間有效。
- [x] **`_suppressFocusSync` 競態條件**：`focusCell()` 改為 `async`，在 `setFocusedCell` 後 `await nextTick()` 再清除 flag，防止 `onCellFocused` microtask 在 flag 清除後才執行。
- [x] **Ctrl+A 後 fillHandle 不更新**：`Ctrl+A` 選取全部後缺少 `updateAllRects()` 呼叫，導致填充柄不出現。
- [x] **CSS 硬編碼顏色**：所有 `rgba(37, 99, 235, ...)` 已改為 `color-mix(in srgb, hsl(var(--primary)) X%, transparent)`，換主題時自動跟隨。
- [x] **`onCellMouseOver` 拖曳效能**：拖曳選取時每移過一格就完整重繪，改用 `requestAnimationFrame` 節流後大幅提升流暢度。
- [x] **滾動 layout thrashing**：`onBodyScroll` 加入 RAF 節流，防止滾動時重複觸發 DOM 計算。
- [x] **Ctrl+點擊未保留第一個點選格**：在 wrapper 的 `mousedown.capture` 先暫停 focus 同步，避免 AG Grid 的 `cell-focused` 在 `cell-mouse-down` 前覆蓋既有單格選取。
- [x] **編輯模式仍顯示 Fill Handle**：加入 `isEditing` 狀態並監聽 `cell-editing-started/stopped`，編輯期間隱藏右下角填充柄。
