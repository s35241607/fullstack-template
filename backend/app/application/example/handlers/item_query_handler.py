from dataclasses import dataclass
from uuid import UUID

from app.domain.example.entities.item import Item
from app.domain.example.repositories.item_repository import ItemRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class GetItemQuery:
    item_id: UUID


@dataclass
class ListItemsQuery:
    pass


class ItemQueryHandler:
    """Handles read operations for Item aggregate (CQRS Query side)."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    async def handle_get(self, query: GetItemQuery) -> Item:
        item = await self._repository.get_by_id(query.item_id)
        if item is None:
            raise EntityNotFoundError("Item", query.item_id)
        return item

    async def handle_list(self, query: ListItemsQuery) -> list[Item]:  # noqa: ARG002
        return await self._repository.get_all()
