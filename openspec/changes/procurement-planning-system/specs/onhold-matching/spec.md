## ADDED Requirements

### Requirement: 查詢 On-hold 候選清單
系統 SHALL 根據 Item 的機型，從 On-hold 模組查詢可配對的 On-hold 訂單清單。

#### Scenario: 成功查詢候選
- **WHEN** 使用者對某 Item 開啟 On-hold 配對面板
- **THEN** 系統回傳與該機型匹配的所有 On-hold 訂單，包含：訂單編號、供應商名稱、可用數量、訂單日期、On-hold 類型（Type A / Type B）、鎖定狀態

#### Scenario: 顯示鎖定狀態
- **WHEN** 查詢候選清單中有訂單已被其他 FCST 鎖定
- **THEN** 該訂單顯示鎖定者資訊（FCST 編號），且不可被選擇

#### Scenario: 無候選訂單
- **WHEN** 該機型在 On-hold 模組中沒有任何可用訂單
- **THEN** 面板顯示空狀態提示

### Requirement: 鎖定 On-hold 訂單
系統 SHALL 允許使用者選擇 On-hold 訂單並鎖定，遵循先選先鎖原則。

#### Scenario: 成功鎖定
- **WHEN** 使用者選擇一或多筆可用的 On-hold 訂單並確認
- **THEN** 系統建立鎖定記錄（onhold_locks），設定到期時間（TTL），Item 的 onhold_a_qty / onhold_b_qty 更新
- **AND** 被鎖定的訂單對其他 FCST 不可用

#### Scenario: 併發搶佔
- **WHEN** 兩個使用者同時嘗試鎖定同一筆 On-hold 訂單
- **THEN** 先提交的使用者成功鎖定，後提交的使用者收到「訂單已被鎖定」錯誤

#### Scenario: 鎖定數量超過需求
- **WHEN** 使用者選擇的 On-hold 訂單總數量超過 Item 剩餘需求（total - transfer）
- **THEN** 系統發出警告提示，但不阻止操作（因 HCEMS 結果可能尚未回覆）

### Requirement: 釋放 On-hold 鎖定
系統 SHALL 支援手動和自動釋放 On-hold 鎖定。

#### Scenario: 手動釋放
- **WHEN** 使用者在 On-hold 面板取消已選擇的訂單
- **THEN** 系統釋放該訂單的鎖定，其他 FCST 可重新選擇

#### Scenario: 撤回時自動釋放
- **WHEN** Item 被撤回
- **THEN** 系統自動釋放此 Item 所有鎖定的 On-hold 訂單

#### Scenario: TTL 到期自動釋放
- **WHEN** On-hold 鎖定記錄到達 expires_at 時間
- **THEN** 系統自動釋放鎖定，通知相關 FCST 的使用者

#### Scenario: Reconciliation 調整釋放
- **WHEN** HCEMS 結果導致超額分配，使用者調整減少 On-hold 數量
- **THEN** 系統釋放多餘的 On-hold 鎖定

### Requirement: On-hold 鎖定到期預警
系統 SHALL 在 On-hold 鎖定即將到期時通知使用者。

#### Scenario: 到期前預警
- **WHEN** On-hold 鎖定距離到期時間不足 7 天
- **THEN** FCST 詳情頁顯示黃色警告 Banner，提示哪些 On-hold 鎖定即將到期
