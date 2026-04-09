# EPS 採購規劃系統 — FCST 需求分配與預算申請流程

## Why

廠內使用者需要在 eCapEx 預算申請前，針對每筆設備需求進行**來源分配**（移轉、On-hold 釋放、預約、正常採購），以精準計算實際需要申請的預算數量。目前這個分配流程缺乏系統化管理，導致：

1. **移轉確認耗時**：HCEMS 移轉查詢需要數週，但又是稽核必要程序，不可跳過
2. **優先順序與時程衝突**：優先度最高的來源（移轉）耗時最長，急迫需求被卡住
3. **手動追蹤困難**：多個 Items 各自在不同分配階段，無法一覽進度
4. **On-hold 資源競爭**：多個 FCST 搶同一批 on-hold 訂單，缺乏鎖定機制
5. **Item 修改連鎖問題**：使用者修改機型或數量後，已完成的分配查詢可能失效

## 系統定位

EPS = **需求分配引擎 (Demand Allocation Engine)**

```
輸入：廠內需求 (FCST Items: 機型 × 數量)
處理：在多個供應管道之間做最佳分配
輸出：一份完整的單據 → 推送到 eCapEx
```

外部系統整合：
- **HCEMS**：移轉機台系統，查詢是否有可移轉設備
- **eCapEx**：集團預算申請系統，接收最終預算申請單據
- **On-hold 模組**：EPS 內部的訂單管理模組（獨立開發）

---

## What Changes (Phase 2: 需求分配流程)

> Phase 1（已完成）：基礎 CRUD — 採購計畫建立、計畫項目管理
> Phase 2（本次）：需求分配流程 — FCST 生命週期、移轉/On-hold/預約/採購分配、eCapEx 串接

### 核心概念

- **FCST (Forecast)**：一份採購預測單，包含一到多個 Items
- **FCST Item**：單一設備需求（機型 × 數量），需經過來源分配
- **來源分配 (Sourcing Allocation)**：將需求數量分配到移轉/On-hold/預約/正常採購
- **1 FCST = 1 eCapEx**：一對一關係

### 需求數量分配模型

每個 FCST Item 的「總需求數量」會被分配到以下來源：

| 來源管道 | 說明 | 預算影響 | 數據來源 |
|---------|------|---------|---------|
| 移轉 (Transfer) | HCEMS 確認可移轉的設備 | ✅ 不需預算 | HCEMS 回傳 check code + 數量 |
| On-hold Type A (直接轉移) | 釋放既有 on-hold 訂單直接使用 | ✅ 扣減預算申請數 | EPS On-hold 模組 |
| On-hold Type B (生意換生意) | 同供應商訂單互換，取消舊訂單換新設備 | ✅ 不影響預算申請 (預算中立) | EPS On-hold 模組 |
| 預約 (Reservation) | 急迫需求，先行通知供應商準備 | ❌ 仍需預算 | 使用者標記 |
| 正常採購 (Purchase) | 無其他來源，直接新購 | ❌ 需預算 | 剩餘數量 |

**預算計算公式**：
```
eCapEx 預算申請數量 = 總需求 - 移轉數量 - OnHold_A數量 - OnHold_B數量
```
> 預約數量仍包含在預算申請數量中（來源是新購，只是處理優先級較高）

### 優先度

```
移轉 (Transfer) > On-hold Release > 預約 (Reserve) > 正常採購 (Purchase)
```

分配衝突時，高優先度來源的數量優先鎖定，低優先度來源需調整。

---

## 系統流程設計

### 一、三軌並行 + 閘門收斂模型

解決「移轉耗時但不可跳過」的核心矛盾：所有不依賴 HCEMS 的工作提前完成，HCEMS 結果回來後立即收斂。

```
FCST 進入 Sourcing
      │
      ├──────────────────────────────────────────────────► 
      │  Track 1: HCEMS 移轉查詢 (非同步，每個 Item 獨立查詢)
      │  系統送出 → 等待回覆(天~週) → 逐一收到 check code
      │
      ├──────────────────►
      │  Track 2: On-hold 配對 (系統帶出候選，User 選擇)
      │  比對 on-hold pool → User 選擇要釋放的訂單 → 鎖定
      │
      ├────►
      │  Track 3: 預約標記 (User 主動操作，即時生效)
      │  User 標記急迫 Item → 記錄預約
      │
      │          ◄── 各 Track 結果陸續回來 ──►
      │
      ▼
  ╔══════════════════════════════════╗
  ║    HCEMS 閘門 (Hard Gate)        ║
  ║    所有 Item 的 HCEMS 都回覆後    ║
  ║    才能進入下一階段               ║
  ╚══════════════════╤═══════════════╝
                     │
                     ▼
              分配調整 (Reconciliation)
              → 檢查是否超額分配
              → User 調整 On-hold 配對
                     │
                     ▼
              確認 & 鎖定 → 送出 eCapEx
```

### 二、FCST 層級狀態機

| 狀態 | 條件 | 可執行操作 |
|------|------|----------|
| **Draft** | 有 Item 尚未送出 HCEMS | 新增/編輯/刪除 Items、啟動分配 |
| **Sourcing** | 至少有 Item 在 HCEMS Pending/Confirmed | 配對 On-hold、標記預約、撤回個別 Items |
| **All Resolved** | 所有 Items 的 HCEMS 已回覆 | 分配調整、確認分配 |
| **Finalized** | 所有 Items 都已確認分配 | 檢視摘要、送出 eCapEx |
| **Submitted** | 已推送 eCapEx | 追蹤狀態 |

> FCST 狀態是所有 Item 狀態的 rollup，任一 Item 被撤回會導致 FCST 退回 Sourcing

### 三、FCST Item 層級狀態機

```
                    ┌──────────────┐
          ┌────────►│   Created    │◄──────────────────────┐
          │         │ (可自由編輯)  │                       │
          │         └──────┬───────┘                       │
          │                │ FCST 啟動分配                   │
          │                ▼                               │
          │       ┌─────────────────┐                      │
          │       │  HCEMS Pending  │                      │
          │       │ (機型+數量凍結)  │───── 撤回 ────────────┤
          │       └────────┬────────┘  (釋放on-hold鎖定,   │
          │                │ 收到 check code   清除預約)     │
          │                ▼                               │
          │       ┌─────────────────┐                      │
          │       │ HCEMS Confirmed │                      │
          │       │  移轉數量確定    │───── 撤回 ────────────┤
          │       └────────┬────────┘                      │
          │                │ User 確認分配                   │
          │                ▼                               │
          │       ┌─────────────────┐                      │
          │       │   Allocated     │───── 撤回 ────────────┘
          │       │ 所有來源數量確定  │
          │       └────────┬────────┘
          │                │ FCST 鎖定送出
          │                ▼
          │       ┌─────────────────┐
          │       │     Locked      │ ← 不可撤回
          │       └────────┬────────┘
          │                ▼
          │       ┌─────────────────┐
          └───────│   Submitted     │ ← 不可撤回
                  └─────────────────┘
```

### 四、Item 可編輯性規則

| Item 狀態 | 改機型 | 改數量 | 刪除 | 配對 On-hold | 標記預約 |
|-----------|-------|-------|------|------------|---------|
| Created | ✅ | ✅ | ✅ | ❌ (未啟動分配) | ❌ |
| HCEMS Pending | 🔒 需撤回 | 🔒 需撤回 | 🔒 需撤回 | ✅ | ✅ |
| HCEMS Confirmed | 🔒 需撤回 | 🔒 需撤回 | 🔒 需撤回 | ✅ | ✅ |
| Allocated | 🔒 需撤回 | 🔒 需撤回 | 🔒 需撤回 | 🔒 需撤回 | 🔒 需撤回 |
| Locked | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |

### 五、撤回機制 (Item-level Revoke)

撤回是**單一 Item 層級**的操作，不影響其他 Items：

1. 此 Item 的 HCEMS 查詢標記作廢（check code 失效）
2. 此 Item 鎖定的 On-hold 訂單全部釋放（其他 FCST 可搶）
3. 預約標記清除
4. Item 狀態回到 `Created`（可自由編輯）
5. 修改後需重新送出 HCEMS 查詢，再等一輪回覆

> 撤回會記錄稽核日誌（誰在什麼時候撤回了什麼、原因）

### 六、分配調整 (Reconciliation)

因 On-hold 配對可能在 HCEMS 結果出來前完成，可能產生超額分配：

```
情境：Item 機型A × 10 台
  On-hold 先配對 → 鎖定 4 台
  HCEMS 後回覆 → 可移轉 8 台
  合計 12 > 10 → 超額！

處理：
  移轉優先鎖定（不可改）→ 8 台
  On-hold 需調整 → 最多只能配 2 台（10 - 8 = 2）
  系統提示 User 調整 On-hold 配對
```

### 七、預約機制

預約是**正交維度**，不影響來源分配邏輯：

- **預約 = 急迫性標記**，附加在 Item 上
- 不改變優先度順序（移轉 > on-hold 仍然成立）
- 不改變預算計算方式
- 用途：
  - 優先處理：On-hold 配對時，預約 Items 優先分配
  - 供應商預通知：可先通知供應商準備
  - 內部排程：產線規劃可先排入
  - 單據標記：eCapEx 上標注哪些是急迫需求

### 八、On-hold 配對流程

1. 系統根據 Item 機型 + 供應商，自動帶出 on-hold pool 中的候選訂單
2. User 從候選清單中選擇要釋放的訂單
3. 選擇後立即鎖定（先選先鎖，其他 FCST 不可再選）
4. 區分 Type A（直接轉移）和 Type B（生意換生意）
5. HCEMS 結果出來後，若超額需調整

### 九、追加預算

追加預算是 FCST 送出 eCapEx 後，一段時間後需要加買的情境：

- 建立**新的 FCST**，帶有「追加」標記
- 關聯原始 FCST（可追溯）
- 走完整的 HCEMS / On-hold / 預約流程
- 送出獨立的 eCapEx 追加預算申請

---

## Capabilities

### New Capabilities (Phase 2)

- `fcst-lifecycle`: FCST 狀態機管理（Draft → Sourcing → All Resolved → Finalized → Submitted），包含啟動分配、鎖定、送出等狀態轉換
- `item-sourcing`: Item 層級的三軌並行分配（HCEMS 查詢、On-hold 配對、預約標記），包含 Item 狀態機（Created → HCEMS Pending → Confirmed → Allocated → Locked）
- `item-revoke`: Item 撤回機制，支援單一 Item 撤回重新編輯，包含連鎖清理（HCEMS 作廢、On-hold 釋放、預約清除）
- `reconciliation`: 分配調整邏輯，處理超額分配場景，依優先度自動計算建議調整方案
- `hcems-integration`: HCEMS 外部系統整合介面，發送移轉查詢、接收 check code 回覆（支援逐一回覆）
- `onhold-matching`: On-hold 訂單配對功能，候選帶出、User 選擇、鎖定/釋放機制
- `reservation`: 預約標記功能，急迫性標記管理
- `budget-calculation`: eCapEx 預算數量計算引擎（總需求 - 移轉 - OnHold_A - OnHold_B）
- `ecapex-integration`: eCapEx 外部系統整合介面，產生並推送預算申請單據
- `fcst-supplement`: 追加預算管理，建立關聯追加 FCST
- `sourcing-dashboard`: 分配進度追蹤 Dashboard，顯示各 Item 即時狀態與整體進度

### Modified Capabilities

- `procurement-plan`: 擴充狀態機（原有 DRAFT/SUBMITTED → 新增 SOURCING/ALL_RESOLVED/FINALIZED），擴充資料模型支援分配欄位
- `plan-item`: 擴充 Item 資料模型，新增分配相關欄位（移轉數量、on-hold 數量、預約標記、check code 等），新增 Item 層級狀態機
- `procurement-ui`: 擴充 UI，新增分配操作介面、進度追蹤、摘要確認頁

---

## 遺漏情境分析 (Edge Cases & Risks)

### 🔴 高風險 — 必須在設計階段解決

#### 1. On-hold 鎖定過期
**情境**：User 鎖定了 on-hold 訂單，但 FCST 遲遲未送出（等 HCEMS 或 User 擱置），導致 on-hold 被長期佔用。
**建議**：On-hold 鎖定設定 TTL（例如 30 天），到期自動釋放並通知 User。或在 Dashboard 上標示「即將到期」的鎖定。

#### 2. HCEMS 查詢超時 / 無回應
**情境**：HCEMS 系統故障或特定 Item 的查詢長時間未回覆，卡住整個 FCST。
**建議**：
- 設定 HCEMS 查詢超時機制（例如 N 週未回覆 → 標記為「超時」）
- 超時的 Item 需要人工介入（聯繫 HCEMS 負責人）
- 系統提供催辦功能或通知機制

#### 3. HCEMS 回覆後的變更（Revocation）
**情境**：HCEMS 已回覆 check code 說可移轉 3 台，但後來 HCEMS 端撤銷了這個移轉機會。
**建議**：
- 是否有可能發生？需確認 HCEMS 的 check code 是否具有「有效期限」或「可撤銷」特性
- 若可能：需設計 HCEMS 變更通知機制，收到撤銷後重新調整分配
- 若不可能（check code = 最終確認）：無需處理

#### 4. 同機型跨 FCST 的資源競爭
**情境**：FCST-A 和 FCST-B 都需要機型X，且 HCEMS 的移轉機會是共享的（只有 5 台可移轉，兩個 FCST 各需 5 台）。
**建議**：
- 移轉數量是由 HCEMS 逐筆回覆，是否由 HCEMS 端控制分配？
- 若 EPS 端需要管理：需建立移轉機會的「額度池」概念
- 若 HCEMS 端管理：EPS 只需接收結果，無需額外處理

### 🟡 中風險 — 應納入設計but可後續迭代

#### 5. On-hold 訂單被外部取消
**情境**：已鎖定的 on-hold 訂單在外部（供應商端或其他系統）被取消。
**建議**：On-hold 模組需有同步機制，檢測到訂單已失效時：
- 自動釋放鎖定
- 通知相關 FCST 的 User
- FCST Item 回到需要重新配對的狀態

#### 6. FCST 取消
**情境**：User 決定整個 FCST 不要了。
**建議**：
- Draft 階段：直接刪除
- Sourcing 階段：需執行全面清理（void 所有 HCEMS 查詢、釋放所有 on-hold 鎖定、清除預約）
- Finalized 階段：需確認是否允許取消（可能已經進行供應商溝通）
- Submitted 階段：不可取消（需透過 eCapEx 端處理）

#### 7. Item 全刪的情境
**情境**：FCST 在 Sourcing 階段，User 把所有 Items 都撤回刪除了。
**建議**：FCST 自動退回 Draft 狀態。若 User 不新增 Items，可以直接取消 FCST。

#### 8. 預約數量 vs Item 數量
**情境**：Item 需要 10 台，User 只標記 4 台為預約。需要追蹤「預約數量」嗎，還是整個 Item 要嘛預約要嘛不預約？
**建議**：
- 簡單方案：整個 Item 層級標記（預約/非預約），不做部分預約
- 靈活方案：允許指定預約數量（Item 10 台，預約其中 4 台）
- 建議先用簡單方案，有需求再擴展

### 🟢 低風險 — 後續迭代處理

#### 9. 併發操作
**情境**：兩個 User 同時操作同一個 FCST（例如同時配對 on-hold）。
**建議**：初版使用樂觀鎖（版本號），後續可加入即時通知。

#### 10. eCapEx 退回
**情境**：eCapEx 審核不通過，退回修改。
**建議**：後續迭代。初版送出後視為終態。

#### 11. 稽核軌跡完整性
**情境**：稽核需要追蹤每一次分配調整、撤回、鎖定的完整歷程。
**建議**：所有關鍵操作（狀態轉換、分配變更、撤回、on-hold 鎖定/釋放）均寫入 audit log。

#### 12. 報表與統計
**情境**：管理層需要看「移轉覆蓋率」「On-hold 利用率」等統計。
**建議**：後續迭代，不在本次 scope。

---

## Impact

- **Backend**:
  - 擴充 `app/domain/procurement/` — 新增狀態機、分配邏輯、撤回機制
  - 新增 `app/domain/sourcing/` — HCEMS 整合、On-hold 配對、預約管理
  - 新增 `app/application/sourcing/` — 分配流程 Command/Query Handlers
  - 新增 `app/infrastructure/external/` — HCEMS API client、eCapEx API client
  - 擴充 Database — 新增分配相關欄位、on-hold 鎖定表、audit log 表
- **Frontend**:
  - 擴充 `views/procurement/` — 分配操作介面、On-hold 選擇 Dialog、預約標記
  - 新增 Sourcing Dashboard — 即時進度追蹤、Item 狀態總覽
  - 新增分配摘要確認頁 — 最終預算計算展示
- **External Integration**:
  - HCEMS API 整合（非同步查詢 + 回覆接收）
  - eCapEx API 整合（單據推送）
- **Database**:
  - 擴充 `plan_items` 表（新增分配欄位）
  - 新增 `onhold_locks` 表
  - 新增 `sourcing_audit_logs` 表
  - Alembic migrations

---

## Open Questions (待確認)

1. **HCEMS check code 是否可被撤銷？** 這決定了我們是否需要設計「HCEMS 變更通知」機制
2. **On-hold 鎖定 TTL 應該設多長？** 30 天？還是依照 HCEMS 平均回覆時間而定？
3. **預約是 Item 層級的 boolean 還是可指定預約數量？** 例如 10 台中只預約 4 台
4. **On-hold Type B（生意換生意）的供應商驗證邏輯？** 是否需要驗證「同供應商」的條件？
5. **HCEMS 移轉機會是否由 HCEMS 端控制分配？** 還是 EPS 需要自行管理移轉額度池？
6. **追加預算的 FCST 是否需要獨立的編號規則？** 例如 FCST-2026-001-S1
7. **eCapEx 退回重審的流程是否需要在 Phase 2 處理？** 還是放到後續迭代？
