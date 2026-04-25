from collections.abc import Sequence
from uuid import UUID

from app.models.notification import Notification
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate


class NotificationService:
    """Service for managing notifications."""

    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def list_notifications(self, unread_only: bool = False) -> Sequence[Notification]:
        return await self.repository.get_notifications(unread_only=unread_only)

    async def get_unread_count(self) -> int:
        return await self.repository.get_unread_count()

    async def create_notification(self, data: NotificationCreate) -> Notification:
        return await self.repository.create(data.model_dump())

    async def mark_as_read(self, notification_id: UUID) -> Notification | None:
        notification = await self.repository.get(notification_id)
        if notification:
            return await self.repository.update(notification, {"is_read": True})
        return None

    async def mark_all_as_read(self) -> None:
        await self.repository.mark_all_as_read()
