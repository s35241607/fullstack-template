from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_notification_service
from app.schemas.notification import NotificationCreate, NotificationRead, UnreadCount
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationRead])
async def list_notifications(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    unread_only: bool = False,
) -> list[NotificationRead]:
    return await service.list_notifications(unread_only=unread_only)


@router.get("/unread-count", response_model=UnreadCount)
async def get_unread_count(
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> UnreadCount:
    count = await service.get_unread_count()
    return UnreadCount(count=count)


@router.post("/", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    data: NotificationCreate,
) -> NotificationRead:
    return await service.create_notification(data)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_read(
    notification_id: UUID,
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationRead:
    notification = await service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> None:
    await service.mark_all_as_read()
