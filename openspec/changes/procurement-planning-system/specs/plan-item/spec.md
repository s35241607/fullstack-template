## ADDED Requirements

### Requirement: 新增計畫項目
系統 SHALL 允許使用者在草稿狀態的採購計畫中新增機台設備項目，包含設備名稱、規格、數量、預估單價與備註。

#### Scenario: 成功新增項目
- **WHEN** 使用者在一筆 DRAFT 計畫中新增項目，提供設備名稱、規格、數量與預估單價
- **THEN** 系統建立項目並關聯至該計畫，初始 sourcing 狀態為 CREATED，回傳項目詳細資料

#### Scenario: 在非草稿計畫中新增項目
- **WHEN** 使用者嘗試在非 DRAFT 狀態的計畫中新增項目
- **THEN** 系統拒絕操作並回傳業務規則錯誤

#### Scenario: 設備名稱為空
- **WHEN** 使用者新增項目時設備名稱為空白
- **THEN** 系統拒絕建立並回傳驗證錯誤

#### Scenario: 數量為零或負數
- **WHEN** 使用者新增項目時數量小於等於零
- **THEN** 系統拒絕建立並回傳驗證錯誤

#### Scenario: 預估單價為負數
- **WHEN** 使用者新增項目時預估單價為負數
- **THEN** 系統拒絕建立並回傳驗證錯誤

### Requirement: 更新計畫項目
系統 SHALL 允許使用者修改 CREATED 狀態的項目資料。

#### Scenario: 成功更新 CREATED 項目
- **WHEN** 使用者更新一筆 sourcing 狀態為 CREATED 的項目資料（設備名稱、規格、數量、預估單價、備註）
- **THEN** 系統更新該項目並回傳更新後的資料

#### Scenario: 更新非 CREATED 狀態的項目
- **WHEN** 使用者嘗試直接更新 sourcing 狀態不是 CREATED 的項目
- **THEN** 系統拒絕操作，提示需先撤回 Item 才能修改

#### Scenario: 更新不存在的項目
- **WHEN** 使用者嘗試更新不存在的項目 ID
- **THEN** 系統回傳 404 錯誤

### Requirement: 刪除計畫項目
系統 SHALL 允許使用者刪除 CREATED 狀態的項目。

#### Scenario: 成功刪除 CREATED 項目
- **WHEN** 使用者刪除一筆 sourcing 狀態為 CREATED 的項目
- **THEN** 系統移除該項目，回傳 204

#### Scenario: 刪除非 CREATED 項目
- **WHEN** 使用者嘗試刪除 sourcing 狀態不是 CREATED 的項目
- **THEN** 系統拒絕操作，提示需先撤回 Item 才能刪除

### Requirement: 計畫項目預估總金額計算
系統 SHALL 自動計算每筆項目的預估小計（數量 × 預估單價），以及計畫的預估總金額。

#### Scenario: 查詢計畫項目時包含小計
- **WHEN** 使用者查詢計畫詳情
- **THEN** 每筆項目回傳預估小計（數量 × 預估單價），計畫回傳所有項目的預估總金額

## MODIFIED Requirements

### Requirement: Item 資料模型擴充（Phase 2）
Item 資料模型新增分配相關欄位。

#### Scenario: Item 包含分配欄位
- **THEN** 每筆 Item 回傳以下分配相關欄位：sourcing_status（CREATED/HCEMS_PENDING/HCEMS_CONFIRMED/ALLOCATED/LOCKED）、transfer_qty、transfer_check_code、onhold_a_qty、onhold_b_qty、is_reserved、purchase_qty、budget_qty、needs_reconciliation
