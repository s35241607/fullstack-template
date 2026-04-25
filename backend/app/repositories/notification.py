from collections.abc import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Notification, session)

    async def get_notifications(self, unread_only: bool = False) -> Sequence[Notification]:
        stmt = select(Notification).order_by(Notification.created_at.desc())
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unread_count(self) -> int:
        stmt = select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def mark_all_as_read(self) -> None:
        stmt = update(Notification).where(Notification.is_read.is_(False)).values(is_read=True)
        await self.session.execute(stmt)
        await self.session.flush()
