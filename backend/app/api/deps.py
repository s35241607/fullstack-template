from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.notification import NotificationRepository
from app.services.notification import NotificationService


def get_notification_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> NotificationRepository:
    return NotificationRepository(session)


def get_notification_service(
    repository: Annotated[NotificationRepository, Depends(get_notification_repository)],
) -> NotificationService:
    return NotificationService(repository)
