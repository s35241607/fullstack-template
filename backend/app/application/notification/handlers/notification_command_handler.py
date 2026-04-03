from dataclasses import dataclass
from uuid import UUID

from app.domain.notification.entities.notification import Notification
from app.domain.notification.repositories.notification_repository import NotificationRepository
from app.domain.notification.value_objects.notification_type import NotificationType
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class MarkReadCommand:
    notification_id: UUID


@dataclass
class MarkAllReadCommand:
    pass


@dataclass
class CreateNotificationCommand:
    title: str
    message: str
    type: str = "INFO"
    link: str | None = None


class NotificationCommandHandler:
    """Handles write operations for Notification entity."""

    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    async def handle_create(self, command: CreateNotificationCommand) -> Notification:
        notification = Notification(
            title=command.title,
            message=command.message,
            type=NotificationType(command.type),
            link=command.link,
        )
        await self._repository.save(notification)
        return notification

    async def handle_mark_read(self, command: MarkReadCommand) -> Notification:
        notification = await self._repository.get_by_id(command.notification_id)
        if notification is None:
            raise EntityNotFoundError("Notification", command.notification_id)
        notification.mark_as_read()
        await self._repository.save(notification)
        return notification

    async def handle_mark_all_read(self, command: MarkAllReadCommand) -> None:  # noqa: ARG002
        await self._repository.mark_all_as_read()
