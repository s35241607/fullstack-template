from dataclasses import dataclass
from uuid import UUID

from app.domain.example.entities.item import Item
from app.domain.example.repositories.item_repository import ItemRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class CreateItemCommand:
    name: str
    description: str = ""


@dataclass
class UpdateItemCommand:
    item_id: UUID
    name: str | None = None
    description: str | None = None


@dataclass
class DeleteItemCommand:
    item_id: UUID


class ItemCommandHandler:
    """Handles write operations for Item aggregate (CQRS Command side)."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    async def handle_create(self, command: CreateItemCommand) -> Item:
        item = Item(name=command.name, description=command.description)
        await self._repository.save(item)
        return item

    async def handle_update(self, command: UpdateItemCommand) -> Item:
        item = await self._repository.get_by_id(command.item_id)
        if item is None:
            raise EntityNotFoundError("Item", command.item_id)
        item.update(name=command.name, description=command.description)
        await self._repository.save(item)
        return item

    async def handle_delete(self, command: DeleteItemCommand) -> None:
        item = await self._repository.get_by_id(command.item_id)
        if item is None:
            raise EntityNotFoundError("Item", command.item_id)
        await self._repository.delete(command.item_id)
