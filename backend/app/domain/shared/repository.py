from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from app.domain.shared.entity import Entity

E = TypeVar("E", bound=Entity)


class Repository(ABC, Generic[E]):
    """Base interface for all Repositories."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> E | None:
        """Retrieve an entity by its ID."""
        ...

    @abstractmethod
    async def save(self, entity: E) -> None:
        """Persist an entity (create or update)."""
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """Remove an entity by its ID."""
        ...
