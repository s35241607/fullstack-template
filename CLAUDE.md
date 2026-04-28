# Fullstack Template — Project Guidelines

Monorepo combining a Vue 3 frontend and a FastAPI backend.

## Commands

### Global
- **Install All**: `pnpm install && cd backend && uv sync`
- **Full Environment (Docker)**: `docker compose up -d --build`

### Frontend (`/frontend`)
- **Dev**: `pnpm dev`
- **Build**: `pnpm build`
- **Lint**: `pnpm lint`

### Backend (`/backend`)
- **Dev (Reload)**: `uv run uvicorn app.main:app --reload --port 8000`
- **Test**: `uv run pytest`
- **Lint/Format (Ruff)**: `uv run ruff check . --fix`
- **Type Check (Mypy)**: `uv run mypy .`

## Architecture & Conventions

### Structure
- `frontend/`: Vue 3 + TypeScript + Tailwind v4 + shadcn-vue.
- `backend/`: Python 3.12 + FastAPI + SQLAlchemy 2.0.
- 
### Shared Rules
- **Commits**: Use Conventional Commits with Chinese descriptions.
- **I18N**: 100% of user-visible text must use i18n keys.
- **Secrets**: Never hardcode. Use `.env` (not committed).

### Sub-directory Guidelines
- Frontend: `frontend/CLAUDE.md`
- Backend: `backend/CLAUDE.md`
