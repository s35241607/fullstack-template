from abc import abstractmethod

from app.domain.notification.entities.notification import Notification
from app.domain.shared.repository import Repository


class NotificationRepository(Repository[Notification]):
    """Repository interface for Notification entity."""

    @abstractmethod
    async def get_all(self, unread_only: bool = False) -> list[Notification]:
        """Retrieve all notifications, optionally filtering unread only."""
        ...

    @abstractmethod
    async def get_unread_count(self) -> int:
        """Return count of unread notifications."""
        ...

    @abstractmethod
    async def mark_all_as_read(self) -> None:
        """Mark all notifications as read."""
        ...
