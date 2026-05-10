# PO Management 系統設計
## 系統架構
幫我整理一個完整的系統架構 SPEC，並且生成 C4 Model，還有 Table schema

目前整個架構會是
- Oracle fusion ERP 雲端，然後每天 ETL PR/PO/RT 等資料到我們 Postgresl fusion schema
- 目前這個系統會有幾個主要功能 交期設定/Target date 設定/On hold 設定/PO 查詢跟相關資訊整理
- dbt 將相關資料使用  stg -> int -> mart + star schema  做資料建模，後續透過 Metabase 做報表分析

## 交期設定
- 可以拆分多筆交期
- 拆分的交期可以是同一個日期，同一個 QTY
- 拆分的 交期的 QTY 可以小數點
- 交期拆分的 QTY 加總要等於 PO Line 的 QTY
- 拆分的交期依照序列號排序，不是依照交期順序
- 交期供應商設定完後會有後續流程給採購或是特定人員審核才會生效

## Target Date 設定
- 可以拆分多筆 Target Date
- 拆分的 Target Date 可以是同一個日期，同一個 QTY
- 拆分的 target date 的 QTY 可以小數點
- Target Date 的設定要可以精準的設定 是這個 PO Line 數量的哪個數量區間，因為未來會去對應現在交期，跟 Target date 設定當下的交期去做 GAP 計算
- Target Date 設定也會有後續流程給採購或特定人員審核才會生效

## Onhold 設定
- 依照 PO Lines 設定要 onhold 的數量
- ON Hold 設定也會有後續流程給採購或特定人員審核才會生效

## 需要注意
- PK 都使用 bigint 自動滾號
- 不管是 oracle fusion/eps 系統/dbt mart，都會在同個 db 不同 schema
- 我這些功能都會有對應的流程，需要一個可以 Audit 的機制，然後流程上會考慮到未來動態改變，比如說這次是給誰審核，未來可能會給某個群的人審核



**請遵守以下規則**
1. 如果有不清楚的 domain 詢問我，不要瞎弄
2. 如果覺得我說的有錯，不要盲目相信
3. 請確保整體架構設計合理，符合企業 production