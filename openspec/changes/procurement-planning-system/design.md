## Context

本專案已具備完整的 DDD + CQRS 架構（以 Item 領域為範例），包含 Domain、Application、Infrastructure、Interfaces 四層分離。後端使用 FastAPI + SQLAlchemy 2.0 async，前端使用 Vue 3 + TypeScript + Tailwind CSS + shadcn-ui。

Phase 1（已完成）已實作基礎的採購計畫 CRUD（ProcurementPlan 聚合根 + PlanItem 子實體）。Phase 2 需要在此基礎上擴充完整的需求分配流程，整合外部系統 HCEMS 和 eCapEx。

## Goals / Non-Goals

**Goals:**
- 實作 FCST 完整生命週期狀態機（Draft → Sourcing → All Resolved → Finalized → Submitted）
- 實作 Item 層級分配狀態機（Created → HCEMS Pending → Confirmed → Allocated → Locked）
- 實作三軌並行分配模型（HCEMS 移轉查詢 / On-hold 配對 / 預約標記）
- 實作 Item 撤回機制（含連鎖清理：HCEMS 作廢、On-hold 釋放、預約清除）
- 實作分配調整（Reconciliation）邏輯，處理超額分配
- 實作 On-hold 訂單配對與鎖定機制（先選先鎖、TTL 到期）
- 實作預算計算引擎（eCapEx 申請數量 = 總需求 - 移轉 - OH_A - OH_B）
- 整合 HCEMS 外部 API（非同步查詢 + 回覆接收）
- 整合 eCapEx 外部 API（單據推送）
- 前端 Sourcing Dashboard、On-hold 配對面板、分配摘要頁

**Non-Goals:**
- 不實作 On-hold 訂單管理模組本身（獨立開發，本系統只做配對消費）
- 不實作 eCapEx 退回重審流程（後續迭代）
- 不實作報表或統計分析（後續迭代）
- 不實作使用者權限角色管理（沿用現有架構）
- 不實作即時通知推播（初版用 polling + toast）

## Decisions

### 1. FCST 狀態機：使用 Domain Event + 狀態枚舉

**決定**: FCST 使用 `FcstStatus` 枚舉（`DRAFT`, `SOURCING`, `ALL_RESOLVED`, `FINALIZED`, `SUBMITTED`），狀態轉換透過 Domain Event 驅動。FCST 狀態為所有 Item 狀態的 rollup。

**理由**: 
- FCST 狀態不是獨立控制的，而是由其所有 Items 的狀態聚合決定
- 例如：所有 Items 的 HCEMS 都回覆 → FCST 自動進入 `ALL_RESOLVED`
- 若任一 Item 被撤回 → FCST 退回 `SOURCING`
- Domain Event 可解耦狀態計算邏輯

**替代方案**: 手動管理 FCST 狀態 — 容易不一致，違反 Single Source of Truth。

### 2. Item 狀態機：獨立於 FCST，支援細粒度控制

**決定**: 每個 PlanItem 擁有獨立的 `ItemSourcingStatus` 枚舉（`CREATED`, `HCEMS_PENDING`, `HCEMS_CONFIRMED`, `ALLOCATED`, `LOCKED`），Item 之間狀態獨立互不阻塞。

**理由**:
- 每個 Item 的 HCEMS 回覆時間不同，需要獨立追蹤
- 撤回是 Item 層級操作，不應影響其他 Items
- On-hold 配對和預約也是 Item 層級操作

**狀態轉換規則**:
```
Created ──(啟動分配)──► HCEMS_Pending
HCEMS_Pending ──(收到 check code)──► HCEMS_Confirmed
HCEMS_Confirmed ──(User 確認分配)──► Allocated
Allocated ──(FCST 鎖定)──► Locked

任何非 Locked 狀態 ──(撤回)──► Created
```

### 3. 撤回機制：Saga Pattern 確保一致性

**決定**: Item 撤回操作使用 Saga Pattern，確保 HCEMS 作廢、On-hold 釋放、預約清除三個動作要麼全部成功，要麼全部回滾。

**理由**: 撤回涉及多個資源的清理，需要保證原子性。若 On-hold 釋放成功但 HCEMS 作廢失敗，會導致資源不一致。

**實作**: Application 層的 `RevokeItemCommandHandler`，順序執行三個清理步驟，任一失敗則回滾。

### 4. On-hold 鎖定：悲觀鎖 + TTL

**決定**: On-hold 配對使用悲觀鎖（SELECT FOR UPDATE），鎖定記錄寫入 `onhold_locks` 表，設定 TTL（預設 30 天）。

**理由**:
- 「先選先鎖」語義需要悲觀鎖保證不會重複鎖定
- TTL 防止 FCST 長期佔用 on-hold 資源
- 需要一個定時任務清理過期鎖定

**資料模型**:
```
onhold_locks:
  id: UUID
  onhold_order_id: UUID (被鎖定的 on-hold 訂單)
  fcst_id: UUID (鎖定者)
  plan_item_id: UUID (對應的 FCST Item)
  locked_at: timestamp
  expires_at: timestamp
  released_at: timestamp (nullable, 釋放時間)
```

### 5. HCEMS 整合：非同步查詢 + Webhook / Polling 回覆

**決定**: HCEMS 查詢為非同步模式。EPS 發送查詢後不等待回覆，透過 Webhook 或 Polling 接收結果。

**理由**: HCEMS 回覆需要數天到數週，不適合同步 API。

**實作方案（依 HCEMS 能力二選一）**:
- **方案 A（Webhook）**: HCEMS 回覆時主動呼叫 EPS 提供的 callback API
- **方案 B（Polling）**: EPS 定時（如每小時）向 HCEMS 查詢未回覆的請求狀態

**資料模型**:
```
hcems_queries:
  id: UUID
  plan_item_id: UUID
  machine_type: string
  requested_qty: int
  query_sent_at: timestamp
  check_code: string (nullable, HCEMS 回覆)
  transfer_qty: int (nullable, HCEMS 回覆的可移轉數量)
  responded_at: timestamp (nullable)
  status: enum (PENDING, CONFIRMED, NO_OPPORTUNITY, TIMEOUT)
```

### 6. 預算計算：Domain Service

**決定**: 預算計算邏輯封裝為 `BudgetCalculationService` Domain Service，不依賴任何外部系統。

**理由**: 
- 計算規則為純業務邏輯：`budget = total - transfer - oh_a - oh_b`
- 作為 Domain Service 方便測試和復用
- 未來計算規則變更時，修改點集中

### 7. eCapEx 整合：Command + Adapter Pattern

**決定**: eCapEx 推送透過 `SubmitToEcapexCommand` 觸發，由 Infrastructure 層的 `EcapexApiAdapter` 實作實際 API 呼叫。

**理由**: 解耦業務邏輯與外部系統實作。初期可用 mock adapter 開發，後期替換為真實 API。

### 8. 分配調整（Reconciliation）：Domain Event 觸發

**決定**: 當 HCEMS 結果回覆時觸發 `HcemsResultReceived` Domain Event，由 `ReconciliationHandler` 檢查是否存在超額分配，若存在則標記 Item 為「需調整」狀態。

**理由**:
- Reconciliation 是因 HCEMS 結果而觸發的業務流程
- 使用 Event-driven 可以解耦 HCEMS 回覆處理和超額檢測
- 超額分配的調整仍需 User 介入，系統只負責偵測和標記

**超額判斷邏輯**:
```python
if item.transfer_qty + item.onhold_a_qty + item.onhold_b_qty > item.total_qty:
    item.mark_needs_reconciliation()
    # 建議調整: 減少 on-hold 配對 (因為 transfer 優先度更高且不可改)
    max_onhold = item.total_qty - item.transfer_qty
    suggested_reduction = (item.onhold_a_qty + item.onhold_b_qty) - max_onhold
```

### 9. 前端架構：Composable + Polling

**決定**: 前端使用 Vue 3 Composable pattern 管理 Sourcing 狀態，HCEMS 進度透過 Polling（每 30 秒）更新。

**理由**:
- 與現有前端架構一致
- WebSocket 對於「數天等一次」的更新頻率過度設計
- Polling 間隔可配置，業務時段頻繁（30s）、非業務時段降頻（5min）

**核心 Composables**:
- `useFcstList()` — FCST 列表管理
- `useFcstSourcing(fcstId)` — 單一 FCST 的分配工作台狀態
- `useOnholdMatching(itemId)` — On-hold 配對面板狀態
- `useAllocationSummary(fcstId)` — 分配摘要和預算計算

### 10. 追加預算：獨立 FCST + 關聯

**決定**: 追加預算建立為獨立的 FCST，透過 `parent_fcst_id` 欄位關聯原始 FCST。追加 FCST 走完整的分配流程。

**理由**: 
- 追加需求的分配邏輯與正常 FCST 完全相同
- 獨立 FCST 避免修改已 Submitted 的歷史資料
- 關聯欄位支持追溯

### 11. 稽核日誌：Event Sourcing Lite

**決定**: 所有關鍵操作（狀態變更、分配調整、撤回、鎖定/釋放）寫入 `sourcing_audit_logs` 表，記錄操作者、時間、操作類型、變更前後值。

**理由**: 移轉確認是稽核必要流程，需要完整的操作軌跡。以追加寫入方式（append-only）確保不可篡改。

## Database Schema (Phase 2 新增/修改)

### 修改: plan_items 表

```sql
ALTER TABLE plan_items ADD COLUMN sourcing_status VARCHAR(20) DEFAULT 'CREATED';
ALTER TABLE plan_items ADD COLUMN transfer_qty INTEGER DEFAULT 0;
ALTER TABLE plan_items ADD COLUMN transfer_check_code VARCHAR(50);
ALTER TABLE plan_items ADD COLUMN onhold_a_qty INTEGER DEFAULT 0;
ALTER TABLE plan_items ADD COLUMN onhold_b_qty INTEGER DEFAULT 0;
ALTER TABLE plan_items ADD COLUMN is_reserved BOOLEAN DEFAULT FALSE;
ALTER TABLE plan_items ADD COLUMN purchase_qty INTEGER DEFAULT 0;
ALTER TABLE plan_items ADD COLUMN budget_qty INTEGER DEFAULT 0;
ALTER TABLE plan_items ADD COLUMN needs_reconciliation BOOLEAN DEFAULT FALSE;
```

### 修改: procurement_plans 表

```sql
ALTER TABLE procurement_plans ADD COLUMN sourcing_progress INTEGER DEFAULT 0; -- X/Y resolved
ALTER TABLE procurement_plans ADD COLUMN parent_fcst_id UUID REFERENCES procurement_plans(id); -- 追加預算
-- status 欄位的 enum 需擴充: DRAFT, SOURCING, ALL_RESOLVED, FINALIZED, SUBMITTED
```

### 新增: hcems_queries 表

```sql
CREATE TABLE hcems_queries (
  id UUID PRIMARY KEY,
  plan_item_id UUID REFERENCES plan_items(id) ON DELETE CASCADE,
  machine_type VARCHAR(100) NOT NULL,
  requested_qty INTEGER NOT NULL,
  query_sent_at TIMESTAMP NOT NULL,
  check_code VARCHAR(50),
  transfer_qty INTEGER,
  responded_at TIMESTAMP,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, CONFIRMED, NO_OPPORTUNITY, TIMEOUT
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 新增: onhold_locks 表

```sql
CREATE TABLE onhold_locks (
  id UUID PRIMARY KEY,
  onhold_order_id UUID NOT NULL,
  fcst_id UUID REFERENCES procurement_plans(id) ON DELETE CASCADE,
  plan_item_id UUID REFERENCES plan_items(id) ON DELETE CASCADE,
  onhold_type VARCHAR(10) NOT NULL, -- TYPE_A, TYPE_B
  locked_qty INTEGER NOT NULL,
  locked_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  released_at TIMESTAMP,
  released_reason VARCHAR(50), -- REVOKED, EXPIRED, RECONCILIATION, FCST_CANCELLED
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 新增: sourcing_audit_logs 表

```sql
CREATE TABLE sourcing_audit_logs (
  id UUID PRIMARY KEY,
  fcst_id UUID NOT NULL,
  plan_item_id UUID,
  action VARCHAR(50) NOT NULL, -- HCEMS_SENT, HCEMS_RECEIVED, ONHOLD_LOCKED, ONHOLD_RELEASED, RESERVED, REVOKED, ALLOCATED, SUBMITTED, etc.
  actor VARCHAR(100) NOT NULL,
  details JSONB, -- 變更前後值、附加資訊
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Domain Model (Phase 2 新增)

```
procurement/ (domain)
├── entities/
│   ├── procurement_plan.py    # 擴充: 新增 sourcing 狀態機邏輯
│   └── plan_item.py           # 擴充: 新增 item sourcing 狀態機 + 分配欄位
├── value_objects/
│   ├── plan_status.py         # 擴充: 新增 SOURCING, ALL_RESOLVED, FINALIZED
│   ├── item_sourcing_status.py  # 新增: CREATED → HCEMS_PENDING → CONFIRMED → ALLOCATED → LOCKED
│   ├── allocation.py          # 新增: 分配結構 VO (transfer, oh_a, oh_b, reserved, purchase)
│   └── onhold_type.py         # 新增: TYPE_A, TYPE_B
├── services/
│   ├── budget_calculation.py  # 新增: 預算計算 Domain Service
│   └── reconciliation.py     # 新增: 超額分配偵測 Domain Service
├── events/
│   ├── hcems_result_received.py    # 新增
│   ├── item_revoked.py             # 新增
│   ├── onhold_locked.py            # 新增
│   ├── onhold_released.py          # 新增
│   ├── fcst_sourcing_started.py    # 新增
│   └── fcst_submitted.py           # 新增
└── repositories/
    ├── procurement_plan_repository.py  # 既有
    ├── hcems_query_repository.py       # 新增
    └── onhold_lock_repository.py       # 新增

sourcing/ (application - CQRS)
├── commands/
│   ├── start_sourcing.py      # 啟動分配 (FCST Draft → Sourcing)
│   ├── revoke_item.py         # 撤回 Item (Saga: HCEMS作廢 + OH釋放 + 預約清除)
│   ├── match_onhold.py        # 配對 On-hold (鎖定)
│   ├── release_onhold.py      # 釋放 On-hold
│   ├── toggle_reservation.py  # 切換預約標記
│   ├── confirm_allocation.py  # 確認 Item 分配
│   ├── finalize_fcst.py       # FCST 所有 Item 確認 → Finalized
│   ├── submit_ecapex.py       # 送出 eCapEx
│   └── receive_hcems_result.py # 接收 HCEMS 回覆 (含 Reconciliation 觸發)
├── queries/
│   ├── get_sourcing_dashboard.py  # Dashboard 資料 (Item 狀態 + 進度)
│   ├── get_onhold_candidates.py   # On-hold 候選清單 (含鎖定狀態)
│   └── get_allocation_summary.py  # 分配摘要 + 預算計算
└── handlers/
    └── ...

infrastructure/
├── external/
│   ├── hcems_api_client.py    # HCEMS API adapter (查詢 + 接收)
│   └── ecapex_api_client.py   # eCapEx API adapter (推送)
├── database/models/
│   ├── hcems_query_model.py   # 新增
│   ├── onhold_lock_model.py   # 新增
│   └── audit_log_model.py     # 新增
└── tasks/
    ├── hcems_polling_task.py   # 定時輪詢 HCEMS (if 無 webhook)
    └── onhold_expiry_task.py   # 定時清理過期 On-hold 鎖定
```

## Risks / Trade-offs

- **[HCEMS 整合模式未定]** → 需確認 HCEMS 支持 Webhook 還是只能 Polling，初期用 mock adapter
- **[On-hold 模組未開發]** → On-hold 配對功能依賴 On-hold 模組提供候選清單 API，初期用 mock data
- **[HCEMS 無回應風險]** → 超時機制 + 人工催辦，無法自動跳過（稽核要求）
- **[On-hold 鎖定 TTL]** → 預設 30 天，可能需要根據實際使用情境調整
- **[並發 On-hold 搶佔]** → 使用悲觀鎖，高併發場景可能有效能影響，但 On-hold 操作頻率低
- **[前端 Polling 效能]** → 30 秒間隔在 Sourcing 階段可接受，需注意多 Tab 場景累積
- **[Reconciliation 自動化]** → 超額偵測自動化，但調整仍需 User 介入（避免自動釋放 User 已選的 On-hold）
