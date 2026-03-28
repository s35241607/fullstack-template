from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.example.handlers.item_command_handler import (
    CreateItemCommand,
    DeleteItemCommand,
    ItemCommandHandler,
    UpdateItemCommand,
)
from app.domain.example.entities.item import Item
from app.domain.shared.exceptions import EntityNotFoundError


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repository: AsyncMock) -> ItemCommandHandler:
    return ItemCommandHandler(mock_repository)


class TestItemCommandHandler:
    async def test_create_item(self, handler: ItemCommandHandler, mock_repository: AsyncMock) -> None:
        command = CreateItemCommand(name="New Item", description="Desc")
        item = await handler.handle_create(command)

        assert item.name == "New Item"
        assert item.description == "Desc"
        mock_repository.save.assert_called_once_with(item)

    async def test_update_item(self, handler: ItemCommandHandler, mock_repository: AsyncMock) -> None:
        existing = Item(name="Old Name")
        mock_repository.get_by_id.return_value = existing

        command = UpdateItemCommand(item_id=existing.id, name="New Name")
        item = await handler.handle_update(command)

        assert item.name == "New Name"
        mock_repository.save.assert_called_once_with(existing)

    async def test_update_nonexistent_item_raises_error(
        self, handler: ItemCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None
        command = UpdateItemCommand(item_id=uuid4(), name="Name")

        with pytest.raises(EntityNotFoundError):
            await handler.handle_update(command)

    async def test_delete_item(self, handler: ItemCommandHandler, mock_repository: AsyncMock) -> None:
        existing = Item(name="To Delete")
        mock_repository.get_by_id.return_value = existing

        command = DeleteItemCommand(item_id=existing.id)
        await handler.handle_delete(command)

        mock_repository.delete.assert_called_once_with(existing.id)

    async def test_delete_nonexistent_item_raises_error(
        self, handler: ItemCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await handler.handle_delete(DeleteItemCommand(item_id=uuid4()))
