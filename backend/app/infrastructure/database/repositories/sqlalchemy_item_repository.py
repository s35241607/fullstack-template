from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.example.entities.item import Item
from app.domain.example.repositories.item_repository import ItemRepository
from app.infrastructure.database.models.item_model import ItemModel


class SqlAlchemyItemRepository(ItemRepository):
    """SQLAlchemy implementation of ItemRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Item | None:
        result = await self._session.get(ItemModel, entity_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[Item]:
        result = await self._session.execute(select(ItemModel))
        return [self._to_entity(model) for model in result.scalars().all()]

    async def save(self, entity: Item) -> None:
        existing = await self._session.get(ItemModel, entity.id)
        if existing:
            existing.name = entity.name
            existing.description = entity.description
        else:
            model = self._to_model(entity)
            self._session.add(model)

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(ItemModel, entity_id)
        if model:
            await self._session.delete(model)

    async def exists_by_name(self, name: str) -> bool:
        result = await self._session.execute(
            select(ItemModel).where(ItemModel.name == name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_entity(model: ItemModel) -> Item:
        item = Item.__new__(Item)
        item.id = model.id
        item.name = model.name
        item.description = model.description
        return item

    @staticmethod
    def _to_model(entity: Item) -> ItemModel:
        return ItemModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )
