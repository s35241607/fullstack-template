## 1. Toast 修復

- [x] 1.1 在 App.vue 中為 Toaster 元件加入 `:theme` prop，綁定 `useDark()` 狀態（dark/light）
- [x] 1.2 驗證 toast 在深色與淺色模式下的樣式正確顯示（info、success、error 各類型）

## 2. 字體系統

- [x] 2.1 在 index.html 中加入 Google Fonts 連結（Inter + Noto Sans TC），使用 `display=swap`
- [x] 2.2 更新 style.css 中的 `body` 與 `@theme` 設定，將 font-family 設為 `'Inter', 'Noto Sans TC', system-ui, sans-serif`

## 3. UI 視覺優化

- [x] 3.1 調整 style.css 中的 CSS 變數色盤，提升深色模式對比度與色彩層次
- [x] 3.2 優化 Card 元件樣式：加入 hover 效果、改善邊框與陰影
- [x] 3.3 優化各頁面表格樣式：統一 header 背景、行高、padding、hover 效果
- [x] 3.4 統一表單元件樣式：input 高度、圓角、聚焦環效果
- [x] 3.5 統一各頁面主內容區域的 padding 與間距

## 4. 通知中心 — 後端 Domain 層

- [x] 4.1 建立 Notification entity（domain/notification/entities/notification.py）
- [x] 4.2 建立 Notification repository 介面（domain/notification/repositories/notification_repository.py）
- [x] 4.3 建立 Notification value objects（type enum 等）

## 5. 通知中心 — 後端 Infrastructure 層

- [x] 5.1 建立 NotificationModel（infrastructure/database/models/notification_model.py）
- [x] 5.2 實作 SQLAlchemy NotificationRepository（infrastructure/database/repositories/notification_repository.py）
- [x] 5.3 在 database session 中註冊新 model

## 6. 通知中心 — 後端 Application 層

- [x] 6.1 建立取得通知列表 query handler（application/notification/queries/）
- [x] 6.2 建立取得未讀計數 query handler
- [x] 6.3 建立標記已讀 command handler（application/notification/commands/）
- [x] 6.4 建立全部標記已讀 command handler

## 7. 通知中心 — 後端 API 層

- [x] 7.1 建立 notification router（interfaces/api/v1/routers/notification_router.py）
- [x] 7.2 實作 GET /api/v1/notifications 端點
- [x] 7.3 實作 GET /api/v1/notifications/unread-count 端點
- [x] 7.4 實作 PATCH /api/v1/notifications/{id}/read 端點
- [x] 7.5 實作 POST /api/v1/notifications/read-all 端點
- [x] 7.6 在 main.py 中註冊 notification_router

## 8. 通知中心 — 前端

- [x] 8.1 建立 useNotifications composable（API 呼叫、狀態管理、未讀計數）
- [x] 8.2 建立 NotificationPanel 元件（Popover 下拉面板、通知列表、空狀態）
- [x] 8.3 更新 AppHeader.vue 鈴鐺圖示：整合 NotificationPanel、顯示未讀 badge 計數
- [x] 8.4 新增 api.ts 中的通知相關 API 函式
- [x] 8.5 實作標記已讀與全部標記已讀互動邏輯
