# Backend Architecture Guidelines (FastAPI + DDD)

## Architecture (Clean / DDD)
- **Domain**: Pure Python. `entities/`, `value_objects/`, `repositories/` (abstract).
- **Application**: Use cases (Handlers). Depends only on Domain interfaces.
- **Infrastructure**: Concrete implementations. `database/` (SQLAlchemy 2.0 ORM), `repositories/`.
- **Interfaces**: API Layer. `routers/`, `schemas/` (Pydantic).

## Dependency Direction
`interfaces → application → domain ← infrastructure`

## Development Order
1. Value Objects -> 2. Entities -> 3. Abstract Repository -> 4. Handlers -> 5. ORM Models -> 6. Concrete Repository -> 7. Pydantic Schemas -> 8. Routers.

## Implementation Rules
- **Domain**: NO imports from `fastapi`, `sqlalchemy`, or `pydantic`. Enforce invariants in `__init__`.
- **Application**: Reside handlers here. Raise `EntityNotFoundError` or `BusinessRuleViolationError`.
- **Infrastructure**: Use `Mapped[]` for SQLAlchemy. `lazy="selectin"` for relationships.
- **API**: Convert domain entities to response schemas using helpers.
- **Schemas**: Response schemas need `from_attributes = True`.

## Tooling
- **Package Manager**: `uv`.
- **Linter/Formatter**: `ruff`.
- **Type Checker**: `mypy --strict`.
- **Database**: PostgreSQL 16 via SQLAlchemy 2.0 asyncpg.

## Lint & Format
Run before commit:
- `uv run ruff check . --fix`
- `uv run ruff format .`
- `uv run mypy .`
