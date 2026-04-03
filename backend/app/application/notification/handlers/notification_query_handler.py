from dataclasses import dataclass

from app.domain.notification.entities.notification import Notification
from app.domain.notification.repositories.notification_repository import NotificationRepository


@dataclass
class ListNotificationsQuery:
    unread_only: bool = False


@dataclass
class GetUnreadCountQuery:
    pass


class NotificationQueryHandler:
    """Handles read operations for Notification entity."""

    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    async def handle_list(self, query: ListNotificationsQuery) -> list[Notification]:
        return await self._repository.get_all(unread_only=query.unread_only)

    async def handle_unread_count(self, query: GetUnreadCountQuery) -> int:  # noqa: ARG002
        return await self._repository.get_unread_count()
