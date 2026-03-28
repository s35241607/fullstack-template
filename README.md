# Fullstack Template

前後端分離專案模板。

| 層級 | 技術 |
|------|------|
| 前端 | Vite + Vue 3 + TypeScript + Vue Router + Pinia |
| 後端 | Python + FastAPI + uv |

---

## 啟動方式

### 後端

```bash
cd backend

# 安裝依賴（首次執行）
uv sync

# 啟動開發伺服器
uv run uvicorn app.main:app --reload --port 8000
```

API 文件：http://localhost:8000/docs

### 前端

```bash
cd frontend

# 安裝依賴（首次執行）
pnpm install

# 啟動開發伺服器
pnpm dev
```

前端：http://localhost:5173

---

## 專案結構

```
fullstack-template/
├── frontend/
│   ├── src/
│   │   ├── router/        # Vue Router
│   │   ├── stores/        # Pinia stores
│   │   ├── views/         # 頁面元件
│   │   ├── components/    # 共用元件
│   │   ├── App.vue
│   │   └── main.ts
│   ├── vite.config.ts     # 含 /api proxy → localhost:8000
│   └── package.json
└── backend/
    ├── app/
    │   ├── main.py        # FastAPI app + CORS
    │   └── routers/
    │       └── example.py # 範例 router（/api/example）
    └── pyproject.toml
```

## API Proxy

前端 `/api/*` 請求會自動代理到後端 `http://localhost:8000`，無需手動處理 CORS。
