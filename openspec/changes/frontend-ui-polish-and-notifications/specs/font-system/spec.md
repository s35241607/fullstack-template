## ADDED Requirements

### Requirement: 全站使用現代化字體
系統 SHALL 載入 Inter（英文）與 Noto Sans TC（繁體中文）字體，並套用為全站預設字體。

#### Scenario: 英文內容使用 Inter 字體
- **WHEN** 頁面渲染包含英文文字的元素
- **THEN** 英文文字 SHALL 以 Inter 字體顯示

#### Scenario: 中文內容使用 Noto Sans TC 字體
- **WHEN** 頁面渲染包含中文文字的元素
- **THEN** 中文文字 SHALL 以 Noto Sans TC 字體顯示

#### Scenario: 字體載入失敗時 fallback
- **WHEN** Google Fonts CDN 無法連線
- **THEN** 系統 SHALL fallback 至系統字體（system-ui, sans-serif），不影響頁面可用性

### Requirement: 字體使用 font-display swap 策略
系統 SHALL 使用 `font-display: swap` 載入字體，避免文字隱形閃爍（FOIT）。

#### Scenario: 字體載入期間顯示 fallback 字體
- **WHEN** 頁面初次載入且字體檔案尚未下載完成
- **THEN** 頁面文字 SHALL 先以 fallback 字體顯示，待字體載入完成後切換，不出現空白文字
