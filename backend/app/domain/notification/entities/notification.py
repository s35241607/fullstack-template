from datetime import datetime

from app.domain.notification.value_objects.notification_type import NotificationType
from app.domain.shared.entity import Entity


class Notification(Entity):
    """通知實體。"""

    def __init__(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        link: str | None = None,
    ) -> None:
        super().__init__()
        self.title = title
        self.message = message
        self.type = type
        self.is_read = False
        self.link = link
        self.created_at = datetime.utcnow()

    def mark_as_read(self) -> None:
        self.is_read = True
