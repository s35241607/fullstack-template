## ADDED Requirements

### Requirement: Sourcing Dashboard 主頁面
系統前端 SHALL 提供 Sourcing Dashboard 頁面，作為 FCST 分配流程的核心工作台。

#### Scenario: 顯示 FCST 資訊和進度
- **WHEN** 使用者進入 FCST 的 Sourcing Dashboard
- **THEN** 頁面顯示 FCST 編號、計畫名稱、目前狀態 Badge、Sourcing 進度（X/Y Items Resolved）

#### Scenario: 顯示分配統計卡片
- **WHEN** Dashboard 載入完成
- **THEN** 頁面頂部顯示四張統計卡片：移轉總數、On-hold 總數、預約總數、正常採購總數

#### Scenario: 顯示 Item 分配表格
- **WHEN** Dashboard 載入完成
- **THEN** 頁面顯示 Item 表格，包含：序號、機型、總數量、移轉數量（含 HCEMS 狀態圖示）、On-hold A 數量、On-hold B 數量、預約標記（星號）、採購數量、Item 狀態 Badge、操作選單

#### Scenario: HCEMS 即時狀態顯示
- **WHEN** Item 的 HCEMS 查詢狀態為 PENDING
- **THEN** 移轉數量欄顯示旋轉 Spinner 圖示
- **WHEN** Item 的 HCEMS 查詢狀態為 CONFIRMED
- **THEN** 移轉數量欄顯示綠色勾號 + 數量

#### Scenario: 超額分配警告
- **WHEN** Item 被標記為 needs_reconciliation
- **THEN** 該行以黃色高亮，採購數量欄顯示警告 icon，Tooltip 提示「移轉已覆蓋部分需求，請調整 On-hold 配對」

#### Scenario: HCEMS 進度自動更新
- **WHEN** Dashboard 處於 Sourcing 狀態
- **THEN** 前端每 30 秒自動刷新 Item 狀態，無需使用者手動重新整理
- **AND** 有 HCEMS 結果更新時顯示 Toast 通知

### Requirement: Item 操作互動
系統前端 SHALL 提供 Item 層級的操作功能。

#### Scenario: 預約標記切換
- **WHEN** 使用者點擊 Item 的星號圖示
- **THEN** 預約標記切換（亮星/暗星），顯示 Toast 確認

#### Scenario: 配對 On-hold
- **WHEN** 使用者在操作選單點擊「配對 On-hold」
- **THEN** 從右側滑入 On-hold 配對面板（Slide-over Drawer），顯示候選清單

#### Scenario: 撤回 Item
- **WHEN** 使用者在操作選單點擊「撤回修改」
- **THEN** 彈出確認 Dialog，顯示撤回影響（HCEMS 作廢 × 1、On-hold 釋放 × N、預約清除）
- **AND** 確認後執行撤回，Item 行變為可編輯狀態

#### Scenario: 確認分配
- **WHEN** 使用者在操作選單點擊「確認分配」
- **THEN** Item 狀態變為 ALLOCATED，該行操作選單只剩「撤回」選項

### Requirement: 底部操作列
系統前端 SHALL 在 Dashboard 底部提供全局操作按鈕。

#### Scenario: 送出按鈕狀態
- **WHEN** 有 Item 尚未 ALLOCATED
- **THEN**「鎖定 & 送出 eCapEx」按鈕為 disabled 狀態，Tooltip 顯示「尚有 N 個 Item 待確認」
- **WHEN** 所有 Items 都 ALLOCATED
- **THEN** 按鈕啟用，點擊後跳轉至分配摘要頁

### Requirement: On-hold 配對面板
系統前端 SHALL 提供 On-hold 配對的 Slide-over Drawer 面板。

#### Scenario: 顯示候選清單
- **WHEN** On-hold 面板開啟
- **THEN** 面板標題顯示機型和需求數量，下方列出所有匹配的 On-hold 訂單卡片

#### Scenario: 篩選 On-hold 類型
- **WHEN** 使用者點擊 Type A / Type B 篩選按鈕
- **THEN** 候選清單只顯示對應類型的訂單

#### Scenario: 已鎖定訂單的顯示
- **WHEN** 候選清單中有訂單已被其他 FCST 鎖定
- **THEN** 該卡片顯示鎖頭圖示和鎖定者 FCST 編號，Checkbox 為 disabled

#### Scenario: 底部彙總
- **WHEN** 使用者勾選/取消候選訂單
- **THEN** 面板底部即時更新已選數量和 Type 分佈

#### Scenario: 確認鎖定
- **WHEN** 使用者點擊「確認 & 鎖定」
- **THEN** 系統鎖定已選訂單，面板關閉，Dashboard 表格更新 On-hold 數量，顯示 Toast 確認

### Requirement: 分配摘要頁
系統前端 SHALL 提供分配摘要頁，作為送出 eCapEx 前的最終確認。

#### Scenario: 顯示分配結構圖表
- **WHEN** 使用者進入分配摘要頁
- **THEN** 左側顯示 Waterfall 圖表，展示從總需求到各來源分配的視覺化結構

#### Scenario: 顯示預算計算
- **WHEN** 分配摘要頁載入
- **THEN** 右側顯示 eCapEx 預算摘要卡片：總需求量、移轉扣減、On-hold A 扣減、On-hold B 扣減、最終預算申請數量（大字綠色強調）

#### Scenario: 顯示明細表
- **WHEN** 分配摘要頁載入
- **THEN** 下方顯示所有 Items 的簡化分配明細表

#### Scenario: 確認送出
- **WHEN** 使用者勾選確認條款並點擊「送出 eCapEx」
- **THEN** 系統鎖定 FCST、推送 eCapEx、顯示成功面並返回列表頁

#### Scenario: 返回調整
- **WHEN** 使用者在摘要頁點擊「返回調整」
- **THEN** 系統導航回 Sourcing Dashboard，不改變任何狀態

### Requirement: FCST 列表頁擴充
系統前端 SHALL 擴充 FCST 列表頁，支援新的狀態和進度追蹤。

#### Scenario: 顯示 Sourcing 進度條
- **WHEN** FCST 處於 SOURCING 狀態
- **THEN** 列表中該 FCST 顯示進度條（X/Y Items Resolved）

#### Scenario: 狀態篩選
- **WHEN** 使用者點擊頂部統計卡片（如「Sourcing: 5」）
- **THEN** 列表自動篩選只顯示該狀態的 FCST

#### Scenario: 狀態 Badge 色彩
- **THEN** 各狀態使用不同顏色：Draft 灰、Sourcing 藍、All Resolved 黃、Finalized 綠、Submitted 紫

### Requirement: 通知與警告
系統前端 SHALL 在關鍵事件發生時提供適當的 UI 回饋。

#### Scenario: HCEMS 結果通知
- **WHEN** Dashboard 輪詢偵測到 Item 的 HCEMS 結果已更新
- **THEN** 顯示 Toast：「Item #N {機型} 移轉確認：{數量} 台可移轉」

#### Scenario: On-hold 鎖定到期預警
- **WHEN** Dashboard 偵測到有 On-hold 鎖定將於 7 天內到期
- **THEN** 頁面頂部顯示黃色 Banner 警告

#### Scenario: 所有 HCEMS 完成通知
- **WHEN** 最後一個 Item 的 HCEMS 結果回覆
- **THEN** 顯示 Toast：「所有 Item 的移轉確認已完成」，FCST 狀態自動更新
