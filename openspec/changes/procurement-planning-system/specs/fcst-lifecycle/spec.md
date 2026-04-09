## ADDED Requirements

### Requirement: 啟動 FCST 分配流程
系統 SHALL 允許使用者將 Draft 狀態的 FCST 啟動分配流程，進入 Sourcing 狀態。啟動時，系統自動對所有 Items 送出 HCEMS 移轉查詢。

#### Scenario: 成功啟動分配
- **WHEN** 使用者對一筆 DRAFT 且至少包含一筆 Item 的 FCST 點擊「啟動分配」
- **THEN** FCST 狀態變為 SOURCING，所有 Items 狀態變為 HCEMS_PENDING，系統對每個 Item 送出 HCEMS 移轉查詢

#### Scenario: 啟動無 Item 的 FCST
- **WHEN** 使用者嘗試啟動一筆沒有 Items 的 FCST
- **THEN** 系統拒絕操作並回傳業務規則錯誤

#### Scenario: 重複啟動已在 Sourcing 的 FCST
- **WHEN** 使用者嘗試啟動非 DRAFT 狀態的 FCST
- **THEN** 系統拒絕操作並回傳狀態錯誤

### Requirement: FCST 狀態自動推進
系統 SHALL 根據所有 Items 的狀態自動推進 FCST 狀態。

#### Scenario: 所有 Items HCEMS 已回覆
- **WHEN** FCST 中最後一個 Item 收到 HCEMS 回覆
- **THEN** FCST 狀態自動從 SOURCING 變為 ALL_RESOLVED

#### Scenario: Item 被撤回導致 FCST 退回
- **WHEN** FCST 處於 ALL_RESOLVED 或 FINALIZED 狀態，且有一個 Item 被撤回
- **THEN** FCST 狀態自動退回 SOURCING

#### Scenario: 所有 Items 確認分配
- **WHEN** FCST 中所有 Items 狀態都變為 ALLOCATED
- **THEN** FCST 可被 User 操作進入 FINALIZED 狀態

### Requirement: 鎖定 FCST 並送出 eCapEx
系統 SHALL 允許使用者將 FINALIZED 的 FCST 鎖定並送出 eCapEx 預算申請。

#### Scenario: 成功送出 eCapEx
- **WHEN** 使用者對 FINALIZED 的 FCST 點擊「送出 eCapEx」並確認
- **THEN** 所有 Items 狀態變為 LOCKED，FCST 狀態變為 SUBMITTED，系統產生 eCapEx 單據並推送至 eCapEx 系統

#### Scenario: 送出時有未確認分配的 Item
- **WHEN** 使用者嘗試送出 FCST，但有 Item 不在 ALLOCATED 狀態
- **THEN** 系統拒絕操作，提示哪些 Items 需要先確認分配

### Requirement: FCST 取消
系統 SHALL 允許使用者取消非 SUBMITTED 狀態的 FCST。

#### Scenario: 取消 Draft FCST
- **WHEN** 使用者取消 DRAFT 狀態的 FCST
- **THEN** 系統刪除 FCST 及其所有 Items

#### Scenario: 取消 Sourcing 中的 FCST
- **WHEN** 使用者取消 SOURCING 狀態的 FCST
- **THEN** 系統作廢所有 HCEMS 查詢、釋放所有 On-hold 鎖定、清除所有預約標記，然後刪除 FCST

#### Scenario: 取消已 Submitted 的 FCST
- **WHEN** 使用者嘗試取消 SUBMITTED 狀態的 FCST
- **THEN** 系統拒絕操作（需透過 eCapEx 端處理）

### Requirement: 追加預算 FCST
系統 SHALL 允許使用者建立追加預算的 FCST，關聯原始 FCST。

#### Scenario: 建立追加 FCST
- **WHEN** 使用者對已 SUBMITTED 的 FCST 點擊「追加預算」
- **THEN** 系統建立新的 FCST，標記為追加預算，自動關聯原始 FCST ID
- **AND** 追加 FCST 走完整的分配流程（HCEMS / On-hold / 預約）
