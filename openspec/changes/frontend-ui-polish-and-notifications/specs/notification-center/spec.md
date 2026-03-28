## ADDED Requirements

### Requirement: 通知資料模型
後端 SHALL 定義 Notification domain entity，包含 id、title、message、type（info/success/warning/error）、is_read、link（可選）、created_at 欄位。

#### Scenario: 建立通知
- **WHEN** 系統呼叫建立通知的 command
- **THEN** 一筆新的 Notification 記錄 SHALL 被儲存至資料庫，is_read 預設為 false，created_at 為當前時間

### Requirement: 取得通知列表 API
系統 SHALL 提供 `GET /api/v1/notifications` 端點，回傳通知列表，支援分頁與篩選。

#### Scenario: 取得所有通知
- **WHEN** 前端發送 `GET /api/v1/notifications`
- **THEN** API SHALL 回傳通知列表，依 created_at 降序排列

#### Scenario: 篩選未讀通知
- **WHEN** 前端發送 `GET /api/v1/notifications?unread_only=true`
- **THEN** API SHALL 僅回傳 is_read 為 false 的通知

### Requirement: 取得未讀通知計數 API
系統 SHALL 提供 `GET /api/v1/notifications/unread-count` 端點，回傳未讀通知數量。

#### Scenario: 取得未讀計數
- **WHEN** 前端發送 `GET /api/v1/notifications/unread-count`
- **THEN** API SHALL 回傳 `{ "count": <number> }` 格式的未讀通知數量

### Requirement: 標記通知已讀 API
系統 SHALL 提供端點允許標記單一或全部通知為已讀。

#### Scenario: 標記單一通知已讀
- **WHEN** 前端發送 `PATCH /api/v1/notifications/{id}/read`
- **THEN** 該通知的 is_read SHALL 被更新為 true

#### Scenario: 標記全部通知已讀
- **WHEN** 前端發送 `POST /api/v1/notifications/read-all`
- **THEN** 所有未讀通知的 is_read SHALL 被更新為 true

#### Scenario: 標記不存在的通知已讀
- **WHEN** 前端發送 `PATCH /api/v1/notifications/{id}/read`，但該 id 不存在
- **THEN** API SHALL 回傳 404 Not Found

### Requirement: 通知下拉面板 UI
前端 SHALL 在 Header 鈴鐺圖示上實作 Popover 下拉面板，顯示近期通知列表。

#### Scenario: 開啟通知面板
- **WHEN** 使用者點擊 Header 的鈴鐺圖示
- **THEN** SHALL 展開通知下拉面板，顯示最近的通知列表

#### Scenario: 通知面板顯示通知內容
- **WHEN** 通知面板開啟且有通知資料
- **THEN** 每筆通知 SHALL 顯示標題、訊息摘要、類型圖示、時間（相對時間格式如「5 分鐘前」），未讀通知有視覺標記

#### Scenario: 通知面板無通知
- **WHEN** 通知面板開啟但無任何通知
- **THEN** SHALL 顯示空狀態提示文字（如「沒有通知」）

### Requirement: 未讀通知計數顯示
Header 鈴鐺圖示 SHALL 顯示未讀通知計數 badge。

#### Scenario: 有未讀通知
- **WHEN** 存在未讀通知
- **THEN** 鈴鐺圖示右上角 SHALL 顯示紅色圓形 badge，內含未讀數量（超過 99 顯示 99+）

#### Scenario: 無未讀通知
- **WHEN** 所有通知已讀或無通知
- **THEN** 鈴鐺圖示 SHALL 不顯示 badge

### Requirement: 通知面板互動操作
通知面板 SHALL 支援標記已讀與全部已讀操作。

#### Scenario: 在面板中標記單一通知已讀
- **WHEN** 使用者點擊通知面板中某筆未讀通知
- **THEN** 該通知 SHALL 被標記為已讀，未讀計數即時更新

#### Scenario: 全部標記已讀
- **WHEN** 使用者點擊通知面板中的「全部標記已讀」按鈕
- **THEN** 所有通知 SHALL 被標記為已讀，未讀計數歸零
