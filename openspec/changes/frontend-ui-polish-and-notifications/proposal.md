## Why

目前前端應用存在多處體驗問題：Toast 通知元件未正確運作（畫面上方出現「正在重新整理…」等訊息未正確顯示於 toast 中）、整體字體使用系統預設缺乏現代感、UI 版面設計粗糙需要視覺優化，以及右上角通知鈴鐺圖示僅為裝飾而無實際功能。這些問題直接影響使用者體驗與產品專業度，需要一次性整合修復。

## What Changes

- **修復 Toast 通知系統**：排查 vue-sonner Toaster 元件配置與 toast 呼叫方式，確保 toast 訊息正確渲染於畫面右上角，包含樣式、位置、主題適配（dark mode）等。
- **升級字體系統**：引入現代化字體組合——英文使用 Inter，中文使用 Noto Sans TC，透過 Google Fonts 載入並套用至全站 CSS 變數與 Tailwind 設定。
- **UI 視覺優化**：全面改善版面設計，包含卡片樣式、表格排版、表單佈局、間距一致性、色彩對比度、以及整體深色主題的視覺品質提升。
- **實作通知中心功能**：從後端 API 到前端 UI 完整實作通知功能——後端新增通知 domain（entity、repository）、API 端點（CRUD + 已讀標記）；前端新增通知下拉面板、未讀計數、通知列表與標記已讀互動。

## Capabilities

### New Capabilities
- `toast-fix`: 修復現有 vue-sonner Toast 通知系統的配置與樣式問題，確保 toast 在各種情境下正確顯示
- `font-system`: 引入 Inter + Noto Sans TC 現代化字體，建立全站字體系統
- `ui-visual-polish`: 全面改善 UI 視覺品質，包含版面佈局、元件樣式、色彩與間距一致性
- `notification-center`: 從後端到前端完整實作通知中心功能，含 API、資料模型、前端 UI 面板

### Modified Capabilities
（無既有 spec 需修改）

## Impact

- **前端**：`style.css`（字體、CSS 變數）、`index.html`（Google Fonts 載入）、`App.vue`（Toaster 配置）、所有 layout 元件（AppHeader、AppSidebar、AppLayout）、各頁面 view 元件的樣式調整、新增通知相關 composable 與 UI 元件
- **後端**：新增 `notification` domain（entities、repositories、value_objects）、application layer（commands、handlers、queries）、infrastructure（database model、repository 實作）、API router
- **依賴**：前端可能新增 `@fontsource/inter`、`@fontsource-variable/noto-sans-tc` 或使用 Google Fonts CDN；後端無新增外部依賴
- **資料庫**：新增 notifications 資料表（SQLite/PostgreSQL）
- **API**：新增 `GET/POST /api/v1/notifications` 等端點
