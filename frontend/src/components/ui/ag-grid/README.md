# AG Grid 客製化封裝元件

基於 **AG Grid Community v35**（`ag-grid-vue3`）的 Vue 3 封裝，在原生功能之上疊加了一套完整的 Excel 風格互動體驗。

## 元件清單

| 檔案 | 說明 |
|------|------|
| `AgGrid.vue` | 主要封裝元件，包含所有 Excel 風格功能 |
| `SearchableSelectEditor.vue` | 可搜尋下拉選單 Cell Editor（popup 彈出式） |
| `index.ts` | 統一匯出入口 |

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
- `rangeSelectedCells`：`Record<string, boolean>` 快速查表，供 `cellClassRules` 套用 `custom-range-selected` 樣式
- `onCellFocused` 事件監聽 AG Grid 原生 focus 移動（方向鍵），同步更新 `selectedRanges`
- `_suppressFocusSync` flag（非 reactive）防止滑鼠選取與程式呼叫 `setFocusedCell` 時觸發迴圈

**視覺呈現：**
- 單格選取：沿用 `.ag-cell-focus` CSS border（primary 色）
- 多格範圍：`selection-range-overlay` div（藍色外框）覆蓋在 grid 之上
- 選取範圍背景：`custom-range-selected` class → `rgba(37, 99, 235, 0.12)` 淡藍色

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

### 高優先度

#### 1. `refreshCells({ force: true })` 效能問題
`updateRangeSelection()` 每次選取變動都強制重繪所有可見格子，當資料列數多時會有明顯卡頓。

**現狀：**
```ts
api.refreshCells({ force: true })
```
**改善方向：**
- 傳入 `rowNodes` 參數，只重繪受影響的列
- 或使用 AG Grid v35 的 `cellStyle` 搭配 reactive 參數（避免手動 refresh）

#### 2. `_suppressFocusSync` 的競態條件
`focusCell()` 中同步設定 flag → 呼叫 AG Grid API → 立即清除 flag，但 `onCellFocused` 是非同步觸發的（AG Grid 內部 microtask），可能在 flag 清除後才觸發。

**現狀：**
```ts
_suppressFocusSync = true
api.setFocusedCell(...)
_suppressFocusSync = false  // 可能過早清除
```
**改善方向：** 改用計數器（`_suppressFocusSyncCount`）或在 `nextTick` 後清除：
```ts
_suppressFocusSync = true
api.setFocusedCell(...)
await nextTick()
_suppressFocusSync = false
```

#### 3. `ModuleRegistry.registerModules` 在模組層級執行
目前在 `<script setup>` 頂層執行，每次 import `AgGrid.vue` 都會重新呼叫（雖然 AG Grid 會去重，仍有不必要的副作用）。

**改善方向：** 移到 `main.ts` 或獨立的 `ag-grid-setup.ts` 中，確保只執行一次。

---

### 中優先度

#### 4. `computeRangeRect` 每次都查 DOM
滾動或選取變動時頻繁呼叫 `querySelector`，沒有快取。

**改善方向：**
- 使用 `WeakMap<Element, DOMRect>` 快取，在 `ResizeObserver` 失效時清除
- 或改用 AG Grid 的 `getCellRendererInstances()` API 取得位置（若有）

#### 5. `gridOptions` prop 型別過於寬鬆
```ts
gridOptions?: Record<string, unknown>
```
**改善方向：**
```ts
import type { GridOptions } from 'ag-grid-community'
gridOptions?: GridOptions<GridRowData>
```

#### 6. `rangeSelectedCells` 資料結構語意不清
`Record<string, boolean>` 中的 `true` 值代表「已選取」，永遠不會是 `false`。

**改善方向：** 改用 `Set<string>`：
```ts
const rangeSelectedCells = ref<Set<string>>(new Set())
// 查詢
rangeSelectedCells.value.has(getCellId(...))
```

#### 7. `onBodyViewportScroll` 三個同步更新
滾動時同步呼叫三個 DOM 計算函式，可能導致 layout thrashing。

**改善方向：** 用 `requestAnimationFrame` 批次合併：
```ts
let _rafId: number | null = null
const onBodyViewportScroll = () => {
  if (_rafId) cancelAnimationFrame(_rafId)
  _rafId = requestAnimationFrame(() => {
    updateFillHandlePosition()
    updateSelectionRects()
    updateCopyRects()
    _rafId = null
  })
}
```

---

### 低優先度

#### 8. 大型函式可抽成 composable
`buildClipboardText`、`applyClipboardMatrix`、`applyFill` 等邏輯與 Vue 響應式系統耦合度低，可抽成 `useGridClipboard.ts`、`useGridFill.ts`，便於單元測試。

#### 9. `parsePastedValue` 型別推斷啟發式規則
現行做法以現有格子值的型別推斷貼入型別（如 `typeof currentValue === 'number'`），對 `null` 初始值的格子無法正確推斷。

**改善方向：** 優先依 `colDef.cellDataType` 決定，再 fallback 至現有值型別。

#### 10. CSS 顏色硬編碼
多處使用 `rgba(37, 99, 235, ...)` 硬編碼藍色，在自訂 primary 色時無法自動跟隨。

**改善方向：** 統一改用 `color-mix(in srgb, hsl(var(--primary)) X%, transparent)` 或 CSS 變數。

---

## 後續功能待辦

### 核心功能

- [ ] **Redo（Ctrl+Y / Ctrl+Shift+Z）**：搭配現有 undo stack 新增 redo stack
- [ ] **Ctrl+D 向下填充**：複製最上方格子的值到選取範圍，仿 Excel 行為
- [ ] **Delete / Backspace 清空選取範圍**：一次清空多格內容（保留 undo 記錄）
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
