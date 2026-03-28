## ADDED Requirements

### Requirement: Toast 訊息在各主題模式下正確顯示
vue-sonner Toaster 元件 SHALL 根據當前主題（dark/light）自動切換 toast 樣式，確保文字可讀性與視覺一致性。

#### Scenario: 深色模式下顯示 toast
- **WHEN** 使用者處於深色模式並觸發一個 success toast
- **THEN** toast 以深色背景、淺色文字、綠色高亮顯示，與深色主題一致

#### Scenario: 淺色模式下顯示 toast
- **WHEN** 使用者處於淺色模式並觸發一個 error toast
- **THEN** toast 以淺色背景、深色文字、紅色高亮顯示，與淺色主題一致

#### Scenario: 主題切換時 toast 即時適配
- **WHEN** 使用者在 toast 可見期間切換主題模式
- **THEN** 後續產生的 toast SHALL 使用新主題的樣式

### Requirement: Toast 位置與互動行為正確
Toaster SHALL 固定於畫面右上角顯示，支援 close button 手動關閉，且多個 toast 可堆疊顯示。

#### Scenario: 多個 toast 同時顯示
- **WHEN** 連續觸發 3 個不同類型的 toast（info、success、error）
- **THEN** 3 個 toast 以堆疊方式在右上角依序顯示，每個都有 close button

#### Scenario: Toast 自動消失
- **WHEN** 一個 toast 被觸發後
- **THEN** toast SHALL 在預設時間（約 4 秒）後自動消失，不遮擋使用者操作
