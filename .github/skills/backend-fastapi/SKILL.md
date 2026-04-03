---
name: backend-fastapi
description: >
  Backend development skill for this project's FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Clean Architecture (DDD) stack.
  USE THIS SKILL whenever the user wants to:
  (A) generate a domain entity, value object, or repository interface,
  (B) review existing backend code for convention/architecture issues,
  (C) scaffold a full backend feature (domain → application → infrastructure → API router).
  Trigger on: "新增 API", "建立 entity", "新增 domain", "新功能後端", "add endpoint", "create model",
  "add route", "審查後端", "review backend", "refactor handler", "add repository", "新增 handler",
  "新增 schema", "write test", "新增測試".
---

This skill enforces the exact Clean Architecture / DDD conventions used throughout this project's backend.
Always follow these patterns precisely — the architecture has strict layer boundaries that must not be crossed.

Read `references/conventions.md` for the full code convention reference before generating any code.
Read `references/review-checklist.md` when performing a review task.

---

## Architecture Overview

```
domain/           ← Pure Python, zero framework dependency
  shared/         ← Entity, Repository[E], ValueObject, exceptions
  <domain>/
    entities/     ← Aggregate roots + child entities
    value_objects/ ← Immutable frozen dataclasses + StrEnum/str,Enum
    repositories/ ← Abstract Repository subclass (ABC)

application/      ← Use cases; depends only on domain interfaces
  <domain>/
    handlers/     ← Command handler class + Query handler class
                     Command/Query dataclasses defined IN the same file

infrastructure/   ← Framework-specific implementations
  config/         ← pydantic-settings Settings class
  database/
    session.py    ← AsyncEngine, async_sessionmaker, get_db_session, Base
    models/       ← SQLAlchemy 2.0 ORM models (Mapped[] syntax)
    repositories/ ← Concrete SqlAlchemy<X>Repository implementations

interfaces/api/v1/
  routers/        ← FastAPI APIRouter per domain
  schemas/        ← Pydantic request/response schemas per domain
```

**Layer dependency rule**: `interfaces → application → domain ← infrastructure`
Infrastructure implements domain interfaces. Application depends on domain interfaces, NOT infrastructure.

---

## Task Detection

Identify which mode applies from the user's request:

| Mode                          | Trigger keywords                                                   | Action                                                        |
| ----------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------- |
| **A — Domain Layer**          | "entity", "value object", "repository interface", "domain", "聚合" | Follow [Domain Layer Generation](#a--domain-layer-generation) |
| **B — Review Code**           | "審查", "review", "check", "audit", "架構問題"                     | Follow [Code Review](#b--code-review)                         |
| **C — Full Feature Scaffold** | "新功能", "add feature", "新增 API", "new domain", "scaffold"      | Follow [Full Feature Scaffold](#c--full-feature-scaffold)     |

If ambiguous, ask once: "你想要 (A) 建立 Domain 層物件、(B) 審查程式碼，或是 (C) 完整新功能 Scaffold？"

---

## A — Domain Layer Generation

Generate domain objects that have **zero** framework imports (no FastAPI, no SQLAlchemy, no Pydantic).

**Steps:**

1. Clarify: domain name, entity fields, business rules/invariants, repository query methods needed.
2. Read `references/conventions.md` sections "Entity Rules" and "Repository Rules".
3. Output files in this order: value objects → entity → repository interface.

**File placement:**

- `app/domain/<domain>/value_objects/<name>.py`
- `app/domain/<domain>/entities/<name>.py`
- `app/domain/<domain>/repositories/<name>_repository.py`

**Never import** from `app.infrastructure`, `app.interfaces`, `fastapi`, `sqlalchemy`, or `pydantic` in domain layer files.

---

## B — Code Review

Perform a structured review. Read `references/review-checklist.md` for the full checklist, then produce a report in this format:

```
## Code Review: <filename>

### ✅ Passes
- ...

### ⚠️ Warnings (should fix)
- ...

### ❌ Errors (must fix)
- ...

### 💡 Suggestions (optional improvements)
- ...
```

Always include concrete fix examples for every ⚠️ and ❌ item.

---

## C — Full Feature Scaffold

Scaffold all layers for a new feature. Work strictly in this order to respect dependency direction:

```
1. domain/<name>/value_objects/   — enums, value objects
2. domain/<name>/entities/        — aggregate root + child entities
3. domain/<name>/repositories/    — abstract repository interface
4. application/<name>/handlers/   — command handler + query handler (+ Command/Query dataclasses)
5. infrastructure/database/models/ — SQLAlchemy ORM model
6. infrastructure/database/repositories/ — concrete SqlAlchemy repository
7. interfaces/api/v1/schemas/     — Pydantic request/response schemas
8. interfaces/api/v1/routers/     — FastAPI APIRouter with endpoints
9. app/main.py                    — register the new router
```

**For each layer**, read the corresponding section in `references/conventions.md` before writing.

**Checklist before finishing:**

- [ ] Domain layer has zero framework imports
- [ ] Entity validates invariants in `__init__` or dedicated `_validate_*` methods
- [ ] Repository interface inherits `Repository[EntityType]` from `app.domain.shared.repository`
- [ ] Handler methods named `handle_<action>`, return domain entities (not schemas)
- [ ] Handler raises `EntityNotFoundError` / `BusinessRuleViolationError` (never HTTPException)
- [ ] SQLAlchemy model uses `Mapped[]` syntax, `lazy="selectin"` for relationships
- [ ] Concrete repository has `_to_entity()` and `_to_model()` static methods
- [ ] `_to_entity()` uses `Entity.__new__()` to bypass `__init__` validation
- [ ] All session operations via injected `AsyncSession`, never creating sessions in handlers
- [ ] Pydantic response schemas have `model_config = {"from_attributes": True}`
- [ ] Update request schemas have all fields as `Optional` (`T | None = None`)
- [ ] Each router endpoint has a `_<entity>_to_response()` helper function
- [ ] Error mapping: `EntityNotFoundError` → 404, `BusinessRuleViolationError` → 422
- [ ] New router included in `app/main.py` with `app.include_router(...)`
