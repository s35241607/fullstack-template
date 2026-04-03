from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class NotificationModel(Base):
    """SQLAlchemy ORM model for Notification entity."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<NotificationModel id={self.id} title={self.title!r}>"
