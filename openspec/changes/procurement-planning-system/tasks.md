## 1. Domain Layer — 領域模型與業務規則

- [x] 1.1 建立 `app/domain/procurement/` 目錄結構（entities、repositories、value_objects）
- [x] 1.2 實作 `PlanStatus` Value Object（DRAFT、SUBMITTED 枚舉）
- [x] 1.3 實作 `PlanItem` 子實體（設備名稱、規格、數量、預估單價、備註，含驗證邏輯）
- [x] 1.4 實作 `ProcurementPlan` 聚合根（名稱、預計採購日期、狀態、項目管理方法）
- [x] 1.5 實作 `ProcurementPlanRepository` 抽象介面（繼承 base Repository，含 get_all）
- [x] 1.6 撰寫 Domain 單元測試：PlanItem 驗證（名稱空白、數量 ≤ 0、單價 < 0）
- [x] 1.7 撰寫 Domain 單元測試：ProcurementPlan 建立、更新、提交、項目管理邏輯

## 2. Application Layer — CQRS Commands & Queries

- [x] 2.1 實作 `ProcurementPlanCommandHandler`（CreatePlan、UpdatePlan、DeletePlan、SubmitPlan）
- [x] 2.2 實作 `PlanItemCommandHandler`（AddItem、UpdateItem、RemoveItem）
- [x] 2.3 實作 `ProcurementPlanQueryHandler`（GetPlan、ListPlans）
- [x] 2.4 撰寫 Application 單元測試：Command Handler 各場景（含業務規則拒絕情境）
- [x] 2.5 撰寫 Application 單元測試：Query Handler 各場景

## 3. Infrastructure Layer — 資料庫模型與 Repository 實作

- [x] 3.1 建立 `ProcurementPlanModel` SQLAlchemy ORM 模型（procurement_plans 表）
- [x] 3.2 建立 `PlanItemModel` SQLAlchemy ORM 模型（plan_items 表，含 foreign key 與 cascade delete）
- [x] 3.3 實作 `SqlAlchemyProcurementPlanRepository`（含 Entity↔Model 雙向映射）
- [x] 3.4 建立 Alembic migration 檔案

## 4. Interfaces Layer — REST API

- [x] 4.1 建立 Pydantic request/response schemas（ProcurementPlan、PlanItem 的 Create、Update、Response）
- [x] 4.2 實作 ProcurementPlan Router（GET list、GET detail、POST create、PUT update、DELETE、POST submit）
- [x] 4.3 實作 PlanItem 巢狀路由（GET items、POST add、PUT update、DELETE remove）
- [x] 4.4 註冊路由至 FastAPI app（main.py）
- [x] 4.5 撰寫 API 整合測試：採購計畫 CRUD + 提交場景
- [x] 4.6 撰寫 API 整合測試：計畫項目 CRUD + 業務規則拒絕場景

## 5. Frontend — 前端頁面與整合

- [x] 5.1 擴充 `services/api.ts`：新增採購計畫與項目的 API 方法與 TypeScript 介面
- [x] 5.2 建立 `composables/useProcurementPlans.ts`：計畫列表狀態管理
- [x] 5.3 建立 `composables/useProcurementPlan.ts`：單一計畫詳情與項目狀態管理
- [x] 5.4 建立 `views/procurement/ProcurementPlansView.vue`：計畫列表頁（含新增、刪除）
- [x] 5.5 建立 `views/procurement/ProcurementPlanDetailView.vue`：計畫詳情頁（含項目 CRUD、提交）
- [x] 5.6 新增前端路由（router/index.ts）：計畫列表與詳情頁
- [x] 5.7 更新側邊欄（AppSidebar.vue）：新增「採購規劃」導航項目
