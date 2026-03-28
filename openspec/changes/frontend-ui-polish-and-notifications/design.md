## Context

本專案為一個 fullstack 管理平台（Vue 3 + FastAPI），前端使用 shadcn-vue + TailwindCSS v4 + Vite 作為技術棧，後端採用 DDD 分層架構（domain → application → infrastructure → interfaces）。目前前端已有基礎佈局（AppLayout、AppHeader、AppSidebar）與採購計畫、BPMN 流程管理等功能頁面，但存在以下問題：

1. **Toast 問題**：vue-sonner 的 `Toaster` 元件已掛載，但 toast 訊息在深色主題下可能未正確適配 theme，且與頁面整體樣式不一致。
2. **字體缺失**：僅使用系統預設字體，中英文字體缺乏設計感。
3. **UI 粗糙**：版面間距、卡片樣式、表格排版缺乏一致性與精緻度。
4. **通知功能空殼**：AppHeader 中有 Bell 圖示與紅點提示，但無實際功能。

後端使用 SQLAlchemy + SQLite（可替換 PostgreSQL），遵循 CQRS 模式（commands/queries + handlers）。

## Goals / Non-Goals

**Goals:**
- 修復 Toast 元件在 dark theme 與 light theme 下的正確顯示
- 引入 Inter（英文）+ Noto Sans TC（中文）字體並套用全站
- 統一提升 UI 視覺品質（卡片、表格、表單、間距、色彩）
- 實作完整通知中心功能（後端 CRUD API + 前端 UI 面板 + 即時未讀計數）

**Non-Goals:**
- 不做 WebSocket 即時推播（本次僅用 polling 或手動刷新）
- 不做推播通知（Push Notification）
- 不重構現有路由結構或 DDD 架構
- 不做使用者偏好設定（通知偏好等）
- 不做 email/SMS 通知整合

## Decisions

### 1. 字體方案：Google Fonts CDN

**選擇**：透過 `index.html` 引入 Google Fonts（Inter + Noto Sans TC）

**替代方案**：
- `@fontsource` npm 套件：需要額外打包，增加 bundle 大小
- 系統字體加強版字型棧：無法保證跨平台一致性

**理由**：Google Fonts CDN 有全球 CDN 快取、免費、zero-config，最適合此專案規模。字體載入使用 `display=swap` 避免 FOIT。

### 2. Toast 修復：vue-sonner theme 適配

**選擇**：在 `<Toaster>` 元件加入 `:theme` prop，綁定到 `isDark` 狀態，確保 dark/light 模式切換時 toast 樣式正確。

**理由**：vue-sonner 內建 `theme` prop 支援 `'dark' | 'light' | 'system'`，直接綁定即可解決問題，不需更換 toast 套件。

### 3. 通知資料模型

**選擇**：後端新增 `Notification` domain entity，包含 `id`、`title`、`message`、`type`（info/success/warning/error）、`is_read`、`link`（可選導航連結）、`created_at` 欄位。

**替代方案**：
- 前端 only（localStorage）：無法跨裝置同步、無持久性
- 第三方通知服務：過度工程、增加外部依賴

**理由**：與現有 DDD 架構保持一致，使用 SQLAlchemy model 對映，維持 CQRS command/query handler 模式。

### 4. 通知 API 設計

**選擇**：RESTful 端點

| Method | Path | 說明 |
| ------ | ---- | ---- |
| GET | `/api/v1/notifications` | 取得通知列表（支援分頁、篩選未讀） |
| GET | `/api/v1/notifications/unread-count` | 取得未讀計數 |
| PATCH | `/api/v1/notifications/{id}/read` | 標記單一通知已讀 |
| POST | `/api/v1/notifications/read-all` | 全部標記已讀 |

**理由**：與現有 `/api/v1/procurement-plans` 風格一致，RESTful 語義清晰。未讀計數獨立端點減少前端輪詢時的資料傳輸量。

### 5. 前端通知 UI

**選擇**：點擊 Header 鈴鐺圖示展開 Popover 下拉面板，顯示近期通知列表。

**技術實作**：使用 radix-vue 的 Popover 元件（已在 shadcn-vue 生態中），搭配新增 `useNotifications` composable 管理狀態與 API 呼叫。

### 6. UI 視覺優化策略

**選擇**：漸進式調整而非全面重寫

- 調整 CSS 變數微調色盤（提升深色模式對比度）
- 統一元件間距（使用 Tailwind spacing scale）
- 改善卡片與表格樣式（加入 hover 效果、更好的 border 處理）
- 優化表單佈局（label 對齊、input 間距）

**理由**：保持現有元件結構不變，僅透過 CSS 與 class 調整達成視覺提升，降低風險。

## Risks / Trade-offs

- **Google Fonts CDN 依賴外部服務** → 使用 `font-display: swap` 確保字體載入失敗時仍有 fallback 系統字體。
- **通知無即時推播** → 使用者需手動刷新或透過 polling 獲取新通知，本次範圍明確為非即時。後續可擴充 WebSocket。
- **UI 調整可能影響現有頁面** → 僅修改全域 CSS 變數與共用元件，避免動到各頁面業務邏輯。逐步驗證各頁面外觀。
- **Toast theme 綁定需要共享 dark mode 狀態** → 利用現有 `@vueuse/core` 的 `useDark` 取得狀態，在 App.vue 層級傳入。
