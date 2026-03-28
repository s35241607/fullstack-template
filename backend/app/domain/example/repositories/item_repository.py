from abc import abstractmethod

from app.domain.example.entities.item import Item
from app.domain.shared.repository import Repository


class ItemRepository(Repository[Item]):
    """Repository interface for Item aggregate."""

    @abstractmethod
    async def get_all(self) -> list[Item]:
        """Retrieve all items."""
        ...

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Check if an item with the given name already exists."""
        ...
