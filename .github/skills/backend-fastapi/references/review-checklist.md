# Backend Code Review Checklist

Use this checklist when performing a code review (Mode B). Check every item and produce a structured report.

---

## Layer Boundary Violations (most critical)

- [ ] **Domain layer** imports nothing from `fastapi`, `sqlalchemy`, `pydantic`, or `app.infrastructure`
- [ ] **Application layer** imports nothing from `fastapi`, `sqlalchemy`, or `app.infrastructure`
- [ ] **Infrastructure layer** does NOT contain business logic (only persistence mechanics)
- [ ] **Routers** do NOT import from `app.infrastructure` directly (only via Depends factories)
- [ ] **Handlers** do NOT raise `HTTPException` — only domain exceptions

## Domain Entity

- [ ] Aggregate root inherits `Entity` from `app.domain.shared.entity`
- [ ] Business invariants validated in `__init__` or `_validate_*` private methods
- [ ] Validation raises `BusinessRuleViolationError` (never `ValueError`, `AssertionError`)
- [ ] State-transition methods on the entity (e.g., `submit()`, `approve()`) — not scattered in handlers
- [ ] Child entities that aren't aggregate roots do NOT inherit `Entity`; they manage their own `uuid4()` id
- [ ] No mutable default arguments (use `field(default_factory=list)` not `[]`)

## Value Objects

- [ ] Enums use `StrEnum` (Python 3.11+) or `str, Enum` — not plain `int` enum
- [ ] Immutable value objects are `@dataclass(frozen=True)` inheriting `ValueObject`
- [ ] Enum values stored in DB as `str` — the entity stores the enum, not the raw string

## Repository Interface (domain layer)

- [ ] Inherits `Repository[EntityType]` from `app.domain.shared.repository`
- [ ] Only abstract methods (`@abstractmethod`) — zero implementation
- [ ] All methods are `async`
- [ ] Returns domain entities, not ORM models or dicts

## Concrete Repository (infrastructure layer)

- [ ] Accepts `AsyncSession` via `__init__`, never creates sessions itself
- [ ] `_to_entity()` uses `Class.__new__(Class)` properly (no validation bypass omission)
- [ ] `_to_model()` converts enum to `.value` when storing as string
- [ ] `save()` handles both insert (new) and update (existing) paths
- [ ] Child entity collections synced correctly in `save()` (avoid orphan ORM objects)
- [ ] Both `_to_entity` and `_to_model` are `@staticmethod`

## SQLAlchemy Models

- [ ] Uses `Mapped[]` type annotation syntax (not legacy `Column(...)` without `Mapped`)
- [ ] All columns have explicit `nullable=False` or `nullable=True`
- [ ] Relationships use `lazy="selectin"` (not `lazy="select"` which breaks async)
- [ ] Enums stored as `Mapped[str]` (not `Mapped[<EnumType>]` in ORM)
- [ ] `__tablename__` is plural snake_case
- [ ] `__repr__` defined
- [ ] `cascade="all, delete-orphan"` on parent side of one-to-many

## Application Handlers

- [ ] Command and Query handlers are separate classes
- [ ] Handler method names follow `handle_<action>` pattern
- [ ] Command/Query dataclasses defined in the same file as the handler
- [ ] Handlers return **domain entities**, never schemas or dicts
- [ ] `EntityNotFoundError` raised (not returning `None`) when entity not found in command handlers
- [ ] No direct database session usage in handlers — only via injected repository

## Pydantic Schemas

- [ ] Request schemas: required fields use `Field(...)`, add `min_length`/`max_length`/`gt`/`ge` constraints
- [ ] Update request schemas: ALL fields `Optional` with `None` default
- [ ] Response schemas: `model_config = {"from_attributes": True}` present
- [ ] No business logic in schemas (no `@validator` / `@model_validator` that duplicates domain rules)
- [ ] UUID fields typed as `UUID`, not `str`
- [ ] Decimal/float fields with `ge=0` where negative values are invalid

## FastAPI Routers

- [ ] `APIRouter(prefix="/<plural-kebab>", tags=["..."])`
- [ ] Separate `get_command_handler` and `get_query_handler` dependency functions
- [ ] Every mutating endpoint (`POST`/`PATCH`/`PUT`/`DELETE`) has `try/except` for domain exceptions
- [ ] `EntityNotFoundError` → `HTTPException(404)`
- [ ] `BusinessRuleViolationError` → `HTTPException(422)`
- [ ] `raise ... from e` used (not bare `raise HTTPException(...)`) to preserve cause
- [ ] `DELETE` endpoint: `status_code=204`, returns `None`
- [ ] `POST` endpoint: `status_code=201`
- [ ] `response_model=` specified on every endpoint
- [ ] `_<entity>_to_response()` is a module-level function, not a method in a class
- [ ] Router registered in `app/main.py` with `app.include_router(..., prefix="/api/v1")`

## Type Safety (mypy strict)

- [ ] No `Any` types without explicit `# type: ignore[...]` justification
- [ ] All function parameters and return types annotated
- [ ] `UUID | None` used instead of `Optional[UUID]` (prefer union syntax)
- [ ] No implicit `Optional` from `= None` without `| None` annotation
- [ ] `list[X]` not `List[X]` (modern lowercase generics)

## Testing

- [ ] Unit tests group related cases into `class Test<Scenario>:`
- [ ] Domain entity tests: plain sync methods (entities are sync), no `async`
- [ ] Application handler tests: `AsyncMock(spec=Repository)` to catch wrong method calls
- [ ] Integration tests use `dependency_overrides` to inject test session
- [ ] No `@pytest.mark.asyncio` decorators (project uses `asyncio_mode = "auto"`)
- [ ] Tests do NOT assert on internal `_private` attributes
- [ ] Each test name describes the scenario: `test_create_with_empty_name_raises`

## Code Style

- [ ] f-strings over `.format()` or `%`
- [ ] `X | Y` union syntax over `Optional[X]` or `Union[X, Y]`
- [ ] No `print()` in non-test code (use proper logging or structured output)
- [ ] Imports organized: stdlib → third-party → local (`app.*`)
- [ ] No circular imports (domain → application → infrastructure is strictly one direction)
