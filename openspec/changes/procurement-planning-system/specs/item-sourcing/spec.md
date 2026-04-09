## ADDED Requirements

### Requirement: HCEMS 移轉查詢
系統 SHALL 在 FCST 啟動分配時，自動對每個 Item 發送 HCEMS 移轉查詢，並接收回覆。

#### Scenario: 成功發送 HCEMS 查詢
- **WHEN** FCST 啟動分配
- **THEN** 系統對每個 Item 的機型和數量向 HCEMS 發送移轉查詢，Item 狀態變為 HCEMS_PENDING

#### Scenario: 接收 HCEMS 回覆 — 有移轉機會
- **WHEN** HCEMS 回覆某 Item 有移轉機會，回傳 check code 和可移轉數量
- **THEN** Item 的 transfer_qty 更新為回覆數量，transfer_check_code 記錄 check code，Item 狀態變為 HCEMS_CONFIRMED
- **AND** 若回覆後發現超額分配，系統標記 Item 為「需調整」

#### Scenario: 接收 HCEMS 回覆 — 全部可移轉
- **WHEN** HCEMS 回覆可移轉數量 ≥ Item 總需求量
- **THEN** Item 的 transfer_qty 設為總需求量，purchase_qty 為 0

#### Scenario: 接收 HCEMS 回覆 — 無移轉機會
- **WHEN** HCEMS 回覆 check code 表示無移轉機會（可移轉數量 = 0）
- **THEN** Item 的 transfer_qty 設為 0，Item 狀態變為 HCEMS_CONFIRMED

#### Scenario: 接收 HCEMS 回覆 — 部分移轉
- **WHEN** HCEMS 回覆可移轉數量 < Item 總需求量且 > 0
- **THEN** Item 的 transfer_qty 設為 HCEMS 回覆數量，剩餘數量繼續走 On-hold / 採購分配

### Requirement: Item 撤回
系統 SHALL 允許使用者撤回非 LOCKED 狀態的 Item，使其回到可編輯的 Created 狀態。

#### Scenario: 成功撤回 Item
- **WHEN** 使用者撤回一個 HCEMS_PENDING 或 HCEMS_CONFIRMED 或 ALLOCATED 狀態的 Item
- **THEN** 系統依序執行：
  1. 將對應的 HCEMS 查詢標記為作廢
  2. 釋放此 Item 所有鎖定的 On-hold 訂單
  3. 清除預約標記
  4. Item 狀態回到 CREATED
  5. 寫入稽核日誌
- **AND** FCST 狀態根據所有 Items 重新計算

#### Scenario: 撤回已 Locked 的 Item
- **WHEN** 使用者嘗試撤回 LOCKED 狀態的 Item
- **THEN** 系統拒絕操作

### Requirement: 預約標記
系統 SHALL 允許使用者在 Sourcing 階段對 Item 進行預約標記，表示此需求具有急迫性。

#### Scenario: 標記預約
- **WHEN** 使用者對 HCEMS_PENDING 或 HCEMS_CONFIRMED 狀態的 Item 切換預約標記
- **THEN** Item 的 is_reserved 設為 true，寫入稽核日誌

#### Scenario: 取消預約
- **WHEN** 使用者對已預約的 Item 取消預約標記
- **THEN** Item 的 is_reserved 設為 false

#### Scenario: 預約不影響預算計算
- **WHEN** Item 標記為預約
- **THEN** 預約不改變 budget_qty 的計算（預約數量仍包含在預算申請中）

### Requirement: 確認 Item 分配
系統 SHALL 允許使用者確認 HCEMS_CONFIRMED 狀態且無分配衝突的 Item 分配。

#### Scenario: 成功確認分配
- **WHEN** 使用者對 HCEMS_CONFIRMED 且 needs_reconciliation = false 的 Item 確認分配
- **THEN** 系統計算最終數量（purchase_qty = total - transfer - oh_a - oh_b），Item 狀態變為 ALLOCATED

#### Scenario: 確認有超額分配的 Item
- **WHEN** 使用者嘗試確認 needs_reconciliation = true 的 Item
- **THEN** 系統拒絕操作，提示需先調整 On-hold 配對

### Requirement: 分配調整（Reconciliation）
系統 SHALL 在 HCEMS 回覆後自動偵測超額分配，並在 User 調整後重新計算。

#### Scenario: 偵測超額分配
- **WHEN** HCEMS 結果回覆後，Item 的 transfer_qty + onhold_a_qty + onhold_b_qty > total_qty
- **THEN** 系統標記 Item 為 needs_reconciliation = true，計算建議調整量

#### Scenario: 調整後消除超額
- **WHEN** 使用者調整 On-hold 配對數量，使 transfer + on-hold ≤ total_qty
- **THEN** 系統自動清除 needs_reconciliation 標記

### Requirement: 預算數量計算
系統 SHALL 自動計算每個 Item 和整個 FCST 的 eCapEx 預算申請數量。

#### Scenario: 計算 Item 預算數量
- **WHEN** Item 的分配數量變更時
- **THEN** budget_qty = total_qty - transfer_qty - onhold_a_qty - onhold_b_qty
- **AND** purchase_qty = budget_qty（其中包含預約和正常採購的數量）

#### Scenario: 計算 FCST 總預算
- **WHEN** 查詢 FCST 分配摘要
- **THEN** 系統回傳所有 Items 的彙總：總需求、總移轉、總 On-hold A、總 On-hold B、總預算申請數量
