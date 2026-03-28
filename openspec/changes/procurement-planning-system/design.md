## Context

本專案已具備完整的 DDD + CQRS 架構（以 Item 領域為範例），包含 Domain、Application、Infrastructure、Interfaces 四層分離。後端使用 FastAPI + SQLAlchemy 2.0 async，前端使用 Vue 3 + TypeScript + Tailwind CSS + shadcn-ui。目前使用者在 ERP 系統開立 PR 前需手動整理機台設備資料，流程冗長且缺乏系統化管理工具。

## Goals / Non-Goals

**Goals:**
- 提供採購計畫 CRUD 功能，讓使用者可建立、管理採購規劃
- 提供計畫內設備項目的新增、編輯、刪除功能
- 遵循現有 DDD + CQRS 架構模式，保持程式碼一致性
- 採用 TDD 開發，確保每個 domain entity/use case 都有對應測試
- 前端提供直覺的操作介面，支援計畫狀態管理

**Non-Goals:**
- 不實作與 ERP 系統的實際 API 串接（屬後續階段）
- 不實作審批流程或 BPMN 工作流整合
- 不實作報表或統計分析功能
- 不實作使用者權限控管（沿用現有架構）
- 不實作設備分類或目錄管理

## Decisions

### 1. 聚合根設計：ProcurementPlan 作為聚合根，PlanItem 作為子實體

**決定**: `ProcurementPlan` 為聚合根，`PlanItem` 為其管理的子實體。所有對 PlanItem 的操作透過 ProcurementPlan 聚合根進行。

**理由**: 計畫項目的生命週期完全附屬於採購計畫，不會獨立存在。遵循 DDD 聚合邊界原則，確保交易一致性。Item 是一對多關係，計畫刪除時項目一併刪除。

**替代方案**: 將 PlanItem 設計為獨立聚合根 — 但項目不具備獨立業務意義，拆開會增加不必要的複雜度。

### 2. 計畫狀態管理：簡單枚舉狀態（Draft → Submitted）

**決定**: 使用 Value Object `PlanStatus` 枚舉（`DRAFT`, `SUBMITTED`），不引入狀態機框架。

**理由**: 現階段只需兩個狀態，保持簡單。已提交的計畫不允許編輯，僅草稿狀態可修改。未來若需要更多狀態（如 Approved、Rejected），可平滑擴展為狀態機。

**替代方案**: 使用 BPMN 工作流引擎管理狀態 — 目前 scope 不需要審批流程，過度設計。

### 3. API 設計：巢狀路由 `/procurement-plans/{id}/items`

**決定**: PlanItem 的 API 路由嵌套在 ProcurementPlan 下，如 `/api/v1/procurement-plans/{plan_id}/items`。

**理由**: 反映聚合根的所有權關係，REST 語義清晰。前端操作時自然會在計畫詳情頁中管理項目。

**替代方案**: 扁平路由 `/api/v1/plan-items?plan_id=xxx` — 語義較弱，不直覺。

### 4. 資料庫：沿用現有 PostgreSQL + SQLAlchemy async pattern

**決定**: 新建 `procurement_plans` 與 `plan_items` 兩張表，使用 foreign key 關聯，配合 Alembic migration。

**理由**: 與現有架構完全一致，無需引入新技術。cascade delete 處理計畫刪除時的項目清理。

### 5. 前端：新增兩個頁面（列表 + 詳情）

**決定**: 建立 `ProcurementPlansView`（計畫列表）和 `ProcurementPlanDetailView`（計畫詳情含項目管理），使用 composable pattern 管理狀態。

**理由**: 遵循現有 Vue 3 Composition API 慣例，與 ItemsView 模式一致。列表頁管理計畫 CRUD，詳情頁管理項目 CRUD。

## Risks / Trade-offs

- **[聚合根內項目數量過多]** → 初期不做分頁，若單一計畫項目超過 100 筆再加入分頁機制
- **[狀態轉換規則簡化]** → 僅 Draft→Submitted 單向流轉，若需退回功能需後續迭代
- **[無 ERP 串接]** → 手動匯出/對照 ERP，後續可透過 API 整合自動化
- **[無並發控制]** → 初版不處理樂觀鎖，若多人同時編輯同一計畫可能覆蓋，後續可加入版本號
