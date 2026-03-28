## Why

目前使用者在 ERP 系統開立採購單（PR）前的前置作業流程過於冗長，導致機台設備的採購時程被壓縮，影響產線規劃與交期。需要一個獨立的採購規劃系統，讓使用者能提前維護計畫採買的機台設備資料，加速 ERP 開單前的準備作業。

## What Changes

- 新增「採購規劃」領域模組，遵循現有 DDD + CQRS 架構模式
- 新增 `ProcurementPlan`（採購計畫）聚合根，用於管理一份完整的採購規劃
- 新增 `PlanItem`（計畫項目）實體，代表計畫中每一筆要採買的機台設備
- 新增完整 REST API（CRUD）供前端操作採購計畫與計畫項目
- 新增前端頁面：採購計畫列表、計畫詳情（含項目管理）
- 新增資料庫表格：`procurement_plans`、`plan_items`
- 整合現有路由與導航，在側邊欄加入採購規劃入口

## Capabilities

### New Capabilities
- `procurement-plan`: 採購計畫的建立、查詢、更新、刪除，包含計畫名稱、預計採購日期、狀態（草稿/已提交）等管理功能
- `plan-item`: 計畫內機台設備項目的新增、編輯、刪除，包含設備名稱、規格、數量、預估金額、備註等欄位管理
- `procurement-ui`: 前端採購規劃頁面，包含計畫列表總覽、計畫詳情頁（含項目 CRUD）、狀態篩選與基本搜尋

### Modified Capabilities

（無既有 spec 需修改）

## Impact

- **Backend**: 新增 `app/domain/procurement/`、`app/application/procurement/`、`app/infrastructure/database/models/`、`app/interfaces/api/v1/` 相關模組
- **Frontend**: 新增 `views/procurement/`、`composables/useProcurement*.ts`、`services/api.ts` 擴充採購 API
- **Database**: 新增 `procurement_plans` 與 `plan_items` 資料表，需 Alembic migration
- **Router**: 前後端路由皆需擴充，側邊欄導航新增採購規劃區塊
- **Dependencies**: 無新增外部依賴，沿用現有 tech stack
