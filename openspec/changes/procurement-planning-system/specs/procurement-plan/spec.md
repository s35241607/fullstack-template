## ADDED Requirements

### Requirement: 建立採購計畫
系統 SHALL 允許使用者建立新的採購計畫，包含計畫名稱與預計採購日期。新建的計畫初始狀態為草稿（DRAFT）。

#### Scenario: 成功建立採購計畫
- **WHEN** 使用者提供有效的計畫名稱與預計採購日期
- **THEN** 系統建立一筆新的採購計畫，狀態為 DRAFT，並回傳計畫詳細資料

#### Scenario: 計畫名稱為空
- **WHEN** 使用者提供空白的計畫名稱
- **THEN** 系統拒絕建立並回傳驗證錯誤

#### Scenario: 計畫名稱超過長度限制
- **WHEN** 使用者提供超過 200 字元的計畫名稱
- **THEN** 系統拒絕建立並回傳驗證錯誤

### Requirement: 查詢採購計畫列表
系統 SHALL 提供查詢所有採購計畫的功能，回傳計畫清單包含基本資訊。

#### Scenario: 查詢所有計畫
- **WHEN** 使用者請求採購計畫列表
- **THEN** 系統回傳所有採購計畫，每筆包含 ID、名稱、預計採購日期、狀態、項目數量、Sourcing 進度

#### Scenario: 無計畫時查詢
- **WHEN** 系統中沒有任何採購計畫且使用者請求列表
- **THEN** 系統回傳空清單

### Requirement: 查詢單一採購計畫
系統 SHALL 允許使用者透過 ID 查詢單一採購計畫的完整資料，包含所有計畫項目。

#### Scenario: 成功查詢計畫
- **WHEN** 使用者以有效 ID 查詢採購計畫
- **THEN** 系統回傳該計畫完整資料，包含所有關聯的計畫項目及其分配狀態

#### Scenario: 查詢不存在的計畫
- **WHEN** 使用者以不存在的 ID 查詢
- **THEN** 系統回傳 404 錯誤

### Requirement: 更新採購計畫
系統 SHALL 允許使用者更新草稿狀態的採購計畫基本資訊（名稱、預計採購日期）。

#### Scenario: 成功更新草稿計畫
- **WHEN** 使用者更新一筆狀態為 DRAFT 的計畫名稱或預計採購日期
- **THEN** 系統更新計畫資料並回傳更新後的計畫

#### Scenario: 更新非草稿狀態的計畫
- **WHEN** 使用者嘗試更新非 DRAFT 狀態的計畫基本資訊
- **THEN** 系統拒絕更新並回傳業務規則錯誤

### Requirement: 刪除採購計畫
系統 SHALL 允許使用者刪除草稿狀態的採購計畫，連同其所有計畫項目一併刪除。

#### Scenario: 成功刪除草稿計畫
- **WHEN** 使用者刪除一筆 DRAFT 狀態的採購計畫
- **THEN** 系統刪除該計畫及其所有關聯項目，回傳 204

#### Scenario: 刪除非草稿計畫
- **WHEN** 使用者嘗試刪除非 DRAFT 狀態的計畫
- **THEN** 系統拒絕操作，提示需先取消計畫

#### Scenario: 刪除不存在的計畫
- **WHEN** 使用者嘗試刪除不存在的計畫
- **THEN** 系統回傳 404 錯誤

## MODIFIED Requirements

### Requirement: 計畫狀態管理（Phase 2 擴充）
系統的計畫狀態從 Phase 1 的 DRAFT/SUBMITTED 擴充為完整的生命週期狀態機。

#### Scenario: 狀態枚舉
- **THEN** 計畫狀態包含：DRAFT、SOURCING、ALL_RESOLVED、FINALIZED、SUBMITTED
- **AND** 狀態轉換規則參見 fcst-lifecycle spec
