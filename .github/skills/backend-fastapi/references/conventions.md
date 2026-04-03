# Backend Code Conventions

Authoritative reference for the project's backend conventions.
Stack: Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · Pydantic v2 · asyncpg · uv · ruff · mypy strict · pytest-asyncio

---

## Entity Rules

### Base Entity (`app/domain/shared/entity.py`)
Every aggregate root and child entity inherits from or follows this pattern:
```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class Entity:
    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### Aggregate Root Pattern
```python
from uuid import UUID, uuid4
from datetime import date
from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import BusinessRuleViolationError
from app.domain.<domain>.value_objects.<status> import <Status>

class <Name>(Entity):
    def __init__(
        self,
        name: str,
        # ... other fields ...
        status: <Status> = <Status>.DRAFT,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())  # allow explicit id for reconstruction
        self._validate_name(name)
        self.name = name
        self.status = status
        self.items: list[ChildEntity] = []

    # Business methods on the entity, not in handlers
    def submit(self) -> None:
        if self.status != <Status>.DRAFT:
            raise BusinessRuleViolationError("Can only submit a DRAFT <name>.")
        self.status = <Status>.SUBMITTED

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("<Name> name cannot be empty.")
        if len(name) > 200:
            raise BusinessRuleViolationError("<Name> name cannot exceed 200 characters.")
```

### Child Entity Pattern (does NOT inherit Entity)
```python
class <ChildName>:
    def __init__(
        self,
        field_one: str,
        quantity: int = 1,
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        if quantity <= 0:
            raise BusinessRuleViolationError("Quantity must be positive.")
        self.field_one = field_one
        self.quantity = quantity
```

### Rules
- Business invariants enforced in `__init__` via `_validate_*` private methods.
- `__init__` raises `BusinessRuleViolationError` (never returns errors).
- State-changing business methods live on the entity (not in handlers).
- Zero framework imports in domain layer.

---

## Value Object Rules

### Enums (use `StrEnum` for Python 3.11+, fallback `str, Enum`)
```python
from enum import StrEnum  # Python 3.11+

class <Name>Status(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"

# OR for broader compatibility:
from enum import Enum
class <Name>Status(str, Enum):
    DRAFT = "DRAFT"
```

### Immutable Value Objects
```python
from dataclasses import dataclass
from app.domain.shared.value_object import ValueObject  # frozen=True dataclass

@dataclass(frozen=True)
class Money(ValueObject):
    amount: float
    currency: str = "TWD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise BusinessRuleViolationError("Amount cannot be negative.")
```

---

## Repository Rules

### Abstract Interface (`domain` layer)
```python
from abc import abstractmethod
from uuid import UUID
from app.domain.shared.repository import Repository
from app.domain.<domain>.entities.<name> import <Name>

class <Name>Repository(Repository[<Name>]):
    """Add domain-specific query methods beyond the base get_by_id/save/delete."""

    @abstractmethod
    async def get_all(self) -> list[<Name>]: ...

    @abstractmethod
    async def get_by_status(self, status: <Status>) -> list[<Name>]: ...
```

Base `Repository[E]` already provides:
```python
async def get_by_id(self, entity_id: UUID) -> E | None: ...
async def save(self, entity: E) -> None: ...
async def delete(self, entity_id: UUID) -> None: ...
```

### Concrete Implementation (`infrastructure` layer)
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.<domain>.repositories.<name>_repository import <Name>Repository
from app.infrastructure.database.models.<name>_model import <Name>Model

class SqlAlchemy<Name>Repository(<Name>Repository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> <Name> | None:
        result = await self._session.get(<Name>Model, entity_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[<Name>]:
        result = await self._session.execute(select(<Name>Model))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, entity: <Name>) -> None:
        existing = await self._session.get(<Name>Model, entity.id)
        if existing:
            existing.name = entity.name
            existing.status = entity.status.value
            # sync child collections here
        else:
            self._session.add(self._to_model(entity))

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(<Name>Model, entity_id)
        if model:
            await self._session.delete(model)

    @staticmethod
    def _to_entity(model: <Name>Model) -> <Name>:
        # Use __new__ to bypass __init__ validation for reconstruction
        obj = <Name>.__new__(<Name>)
        obj.id = model.id
        obj.name = model.name
        obj.status = <Status>(model.status)
        obj.items = [...]  # map child models
        return obj

    @staticmethod
    def _to_model(entity: <Name>) -> <Name>Model:
        return <Name>Model(
            id=entity.id,
            name=entity.name,
            status=entity.status.value,
        )
```

**Key rule**: `_to_entity()` uses `Class.__new__(Class)` to bypass `__init__` — this is intentional for reconstructing persisted entities without re-running validation.

---

## SQLAlchemy Model Rules

```python
from sqlalchemy import String, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import date
from app.infrastructure.database.session import Base

class <Name>Model(Base):
    __tablename__ = "<plural_snake_case>"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    # One-to-many: always lazy="selectin" for eager loading
    items: Mapped[list["<Child>Model"]] = relationship(
        "<Child>Model",
        back_populates="<parent>",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<<Name>Model id={self.id} name={self.name!r}>"

class <Child>Model(Base):
    __tablename__ = "<plural_child>"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    parent_id: Mapped[UUID] = mapped_column(ForeignKey("<parent_table>.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    parent: Mapped["<Name>Model"] = relationship("<Name>Model", back_populates="items")
```

**Rules:**
- Use **SQLAlchemy 2.0 `Mapped[]`** syntax — never legacy `Column(...)` without `Mapped`.
- All columns explicitly set `nullable=False` or `nullable=True`.
- Enum values stored as `str` in DB (`status: Mapped[str]`), converted in `_to_entity()`.
- `lazy="selectin"` for all relationships (avoids `MissingGreenlet` in async context).
- `__repr__` always defined.

---

## Application Handler Rules

### Command/Query Dataclasses (defined IN the handler file)
```python
from dataclasses import dataclass
from uuid import UUID
from datetime import date

@dataclass
class Create<Name>Command:
    name: str
    planned_date: date

@dataclass
class Update<Name>Command:
    entity_id: UUID
    name: str | None = None
    planned_date: date | None = None

@dataclass
class Get<Name>Query:
    entity_id: UUID

@dataclass
class List<Name>Query:
    pass  # empty dataclass when no filter params
```

### Command Handler
```python
from app.domain.<domain>.repositories.<name>_repository import <Name>Repository
from app.domain.shared.exceptions import EntityNotFoundError

class <Name>CommandHandler:
    def __init__(self, repository: <Name>Repository) -> None:
        self._repository = repository

    async def handle_create(self, command: Create<Name>Command) -> <Name>:
        entity = <Name>(name=command.name, planned_date=command.planned_date)
        await self._repository.save(entity)
        return entity

    async def handle_update(self, command: Update<Name>Command) -> <Name>:
        entity = await self._repository.get_by_id(command.entity_id)
        if entity is None:
            raise EntityNotFoundError("<Name>", command.entity_id)
        entity.update(name=command.name, planned_date=command.planned_date)
        await self._repository.save(entity)
        return entity

    async def handle_delete(self, entity_id: UUID) -> None:
        entity = await self._repository.get_by_id(entity_id)
        if entity is None:
            raise EntityNotFoundError("<Name>", entity_id)
        await self._repository.delete(entity_id)
```

### Query Handler
```python
class <Name>QueryHandler:
    def __init__(self, repository: <Name>Repository) -> None:
        self._repository = repository

    async def handle_get(self, query: Get<Name>Query) -> <Name>:
        entity = await self._repository.get_by_id(query.entity_id)
        if entity is None:
            raise EntityNotFoundError("<Name>", query.entity_id)
        return entity

    async def handle_list(self, query: List<Name>Query) -> list[<Name>]:
        return await self._repository.get_all()
```

**Rules:**
- Method names: `handle_create`, `handle_update`, `handle_delete`, `handle_get`, `handle_list`.
- Handlers return **domain entities**, never schemas.
- Handlers raise `EntityNotFoundError` / `BusinessRuleViolationError` — never `HTTPException`.
- Handlers receive the repository via `__init__`, never create sessions themselves.

---

## Pydantic Schema Rules

Location: `app/interfaces/api/v1/schemas/<domain>_schemas.py`

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date

# ── Request Schemas ───────────────────────────────────────────────────────────

class <Name>CreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    planned_date: date

class <Name>UpdateRequest(BaseModel):
    # ALL fields Optional for partial updates
    name: str | None = Field(default=None, min_length=1, max_length=200)
    planned_date: date | None = None

# ── Response Schemas ──────────────────────────────────────────────────────────

class <Child>Response(BaseModel):
    id: UUID
    name: str
    quantity: int
    model_config = {"from_attributes": True}

class <Name>Response(BaseModel):
    id: UUID
    name: str
    status: str
    items: list[<Child>Response]
    model_config = {"from_attributes": True}   # REQUIRED on response schemas
```

**Rules:**
- Request schemas use `Field(...)` for required fields and add validation constraints.
- Update request schemas — ALL fields `Optional` with `None` default.
- Response schemas MUST have `model_config = {"from_attributes": True}`.
- Separate base → create → update → response inheritance only when it reduces duplication significantly.

---

## FastAPI Router Rules

Location: `app/interfaces/api/v1/routers/<domain>_router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.repositories.<name>_repository import SqlAlchemy<Name>Repository
from app.application.<domain>.handlers.<name>_handler import (
    <Name>CommandHandler,
    <Name>QueryHandler,
    Create<Name>Command,
    Update<Name>Command,
    Get<Name>Query,
    List<Name>Query,
)
from app.interfaces.api.v1.schemas.<domain>_schemas import (
    <Name>CreateRequest,
    <Name>UpdateRequest,
    <Name>Response,
)
from app.domain.shared.exceptions import EntityNotFoundError, BusinessRuleViolationError

router = APIRouter(prefix="/<plural-kebab>", tags=["<plural-kebab>"])

# ── Dependency Factories ──────────────────────────────────────────────────────

def _get_repository(session: AsyncSession) -> SqlAlchemy<Name>Repository:
    return SqlAlchemy<Name>Repository(session)

def get_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> <Name>CommandHandler:
    return <Name>CommandHandler(_get_repository(session))

def get_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> <Name>QueryHandler:
    return <Name>QueryHandler(_get_repository(session))

# ── Entity → Response Converter ───────────────────────────────────────────────

def _<name>_to_response(entity: <Name>) -> <Name>Response:
    return <Name>Response(
        id=entity.id,
        name=entity.name,
        status=entity.status.value,
        items=[...],
    )

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[<Name>Response])
async def list_<plural>(
    handler: <Name>QueryHandler = Depends(get_query_handler),
) -> list[<Name>Response]:
    entities = await handler.handle_list(List<Name>Query())
    return [_<name>_to_response(e) for e in entities]

@router.post("/", response_model=<Name>Response, status_code=status.HTTP_201_CREATED)
async def create_<name>(
    body: <Name>CreateRequest,
    handler: <Name>CommandHandler = Depends(get_command_handler),
) -> <Name>Response:
    try:
        entity = await handler.handle_create(Create<Name>Command(name=body.name, ...))
        return _<name>_to_response(entity)
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e

@router.get("/{entity_id}", response_model=<Name>Response)
async def get_<name>(
    entity_id: UUID,
    handler: <Name>QueryHandler = Depends(get_query_handler),
) -> <Name>Response:
    try:
        entity = await handler.handle_get(Get<Name>Query(entity_id=entity_id))
        return _<name>_to_response(entity)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

@router.patch("/{entity_id}", response_model=<Name>Response)
async def update_<name>(
    entity_id: UUID,
    body: <Name>UpdateRequest,
    handler: <Name>CommandHandler = Depends(get_command_handler),
) -> <Name>Response:
    try:
        entity = await handler.handle_update(Update<Name>Command(entity_id=entity_id, ...))
        return _<name>_to_response(entity)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_<name>(
    entity_id: UUID,
    handler: <Name>CommandHandler = Depends(get_command_handler),
) -> None:
    try:
        await handler.handle_delete(entity_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
```

**Error mapping:**
| Domain Exception | HTTP Status |
|-----------------|------------|
| `EntityNotFoundError` | 404 Not Found |
| `BusinessRuleViolationError` | 422 Unprocessable Entity |

**Rules:**
- One `APIRouter` per domain, prefix in plural kebab-case.
- Separate `get_command_handler` and `get_query_handler` dependency functions.
- Each endpoint has a dedicated `try/except` mapping domain exceptions to HTTP.
- DELETE returns `None` with `status_code=204`.
- The `_<name>_to_response()` helper is a module-level function, not a method.

---

## Testing Rules

### Unit Test — Domain Entity
```python
# tests/unit/domain/test_<name>.py
import pytest
from datetime import date
from app.domain.<domain>.entities.<name> import <Name>
from app.domain.shared.exceptions import BusinessRuleViolationError

class Test<Name>:
    def test_create_with_valid_data(self) -> None:
        entity = <Name>(name="Valid Name", planned_date=date(2026, 6, 1))
        assert entity.name == "Valid Name"

    def test_create_with_empty_name_raises(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            <Name>(name="", planned_date=date(2026, 6, 1))

    def test_business_action(self) -> None:
        entity = <Name>(name="Test", planned_date=date(2026, 6, 1))
        entity.submit()
        assert entity.status == <Status>.SUBMITTED
```

### Unit Test — Application Handler
```python
# tests/unit/application/test_<name>_handler.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=<Name>Repository)

@pytest.fixture
def handler(mock_repository: AsyncMock) -> <Name>CommandHandler:
    return <Name>CommandHandler(mock_repository)

class TestCreate<Name>:
    async def test_creates_and_saves(self, handler, mock_repository) -> None:
        entity = await handler.handle_create(Create<Name>Command(name="Test", ...))
        assert entity.name == "Test"
        mock_repository.save.assert_called_once_with(entity)

    async def test_not_found_raises(self, handler, mock_repository) -> None:
        mock_repository.get_by_id.return_value = None
        with pytest.raises(EntityNotFoundError):
            await handler.handle_update(Update<Name>Command(entity_id=uuid4(), name="New"))
```

### Integration Test — API Endpoint
```python
# tests/integration/interfaces/test_<name>_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.infrastructure.database.session import get_db_session

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db_session] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

async def test_create_<name>(client: AsyncClient) -> None:
    response = await client.post("/<plural>/", json={"name": "Test", ...})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
```

**Rules:**
- `asyncio_mode = "auto"` in `pyproject.toml` — all async tests work without `@pytest.mark.asyncio`.
- Test classes group related scenarios: `class TestCreate<Name>:`, `class TestUpdate<Name>:`.
- Use `AsyncMock(spec=Repository)` for handler unit tests.
- Integration tests use `ASGITransport` + `dependency_overrides` to inject test DB session.
- `conftest.py` provides `db_session` fixture using in-memory SQLite.

---

## Infrastructure Config Rules

```python
# app/infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Backend API"
    debug: bool = False
    db_url: str = "postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db"
    db_echo: bool = False

    model_config = {"env_file": ".env"}

settings = Settings()  # module-level singleton — import this everywhere
```

Use `from app.infrastructure.config.settings import settings` everywhere. Never use `os.environ` directly.
