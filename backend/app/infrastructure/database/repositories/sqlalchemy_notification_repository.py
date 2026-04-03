from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notification.entities.notification import Notification
from app.domain.notification.repositories.notification_repository import NotificationRepository
from app.domain.notification.value_objects.notification_type import NotificationType
from app.infrastructure.database.models.notification_model import NotificationModel


class SqlAlchemyNotificationRepository(NotificationRepository):
    """SQLAlchemy implementation of NotificationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Notification | None:
        result = await self._session.get(NotificationModel, entity_id)
        return self._to_entity(result) if result else None

    async def get_all(self, unread_only: bool = False) -> list[Notification]:
        stmt = select(NotificationModel).order_by(NotificationModel.created_at.desc())
        if unread_only:
            stmt = stmt.where(NotificationModel.is_read == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_unread_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(NotificationModel)
            .where(
                NotificationModel.is_read == False  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, entity: Notification) -> None:
        existing = await self._session.get(NotificationModel, entity.id)
        if existing:
            existing.title = entity.title
            existing.message = entity.message
            existing.type = entity.type.value
            existing.is_read = entity.is_read
            existing.link = entity.link
            existing.created_at = entity.created_at
        else:
            model = self._to_model(entity)
            self._session.add(model)

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(NotificationModel, entity_id)
        if model:
            await self._session.delete(model)

    async def mark_all_as_read(self) -> None:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        await self._session.execute(stmt)

    @staticmethod
    def _to_entity(model: NotificationModel) -> Notification:
        entity = Notification.__new__(Notification)
        entity.id = model.id
        entity.title = model.title
        entity.message = model.message
        entity.type = NotificationType(model.type)
        entity.is_read = model.is_read
        entity.link = model.link
        entity.created_at = model.created_at
        return entity

    @staticmethod
    def _to_model(entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            title=entity.title,
            message=entity.message,
            type=entity.type.value,
            is_read=entity.is_read,
            link=entity.link,
            created_at=entity.created_at,
        )
