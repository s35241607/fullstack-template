from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.notification.handlers.notification_command_handler import (
    CreateNotificationCommand,
    MarkAllReadCommand,
    MarkReadCommand,
    NotificationCommandHandler,
)
from app.application.notification.handlers.notification_query_handler import (
    GetUnreadCountQuery,
    ListNotificationsQuery,
    NotificationQueryHandler,
)
from app.domain.notification.entities.notification import Notification
from app.domain.shared.exceptions import EntityNotFoundError
from app.infrastructure.database.repositories.sqlalchemy_notification_repository import (
    SqlAlchemyNotificationRepository,
)
from app.infrastructure.database.session import get_db_session
from app.interfaces.api.v1.schemas.notification_schema import (
    NotificationCreateRequest,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _get_repository(session: AsyncSession) -> SqlAlchemyNotificationRepository:
    return SqlAlchemyNotificationRepository(session)


def get_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationQueryHandler:
    return NotificationQueryHandler(_get_repository(session))


def get_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationCommandHandler:
    return NotificationCommandHandler(_get_repository(session))


def _to_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        type=notification.type.value,
        is_read=notification.is_read,
        link=notification.link,
        created_at=notification.created_at,
    )


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    handler: NotificationQueryHandler = Depends(get_query_handler),
) -> list[NotificationResponse]:
    notifications = await handler.handle_list(ListNotificationsQuery(unread_only=unread_only))
    return [_to_response(n) for n in notifications]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    handler: NotificationQueryHandler = Depends(get_query_handler),
) -> UnreadCountResponse:
    count = await handler.handle_unread_count(GetUnreadCountQuery())
    return UnreadCountResponse(count=count)


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    body: NotificationCreateRequest,
    handler: NotificationCommandHandler = Depends(get_command_handler),
) -> NotificationResponse:
    notification = await handler.handle_create(
        CreateNotificationCommand(
            title=body.title,
            message=body.message,
            type=body.type,
            link=body.link,
        )
    )
    return _to_response(notification)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: UUID,
    handler: NotificationCommandHandler = Depends(get_command_handler),
) -> NotificationResponse:
    try:
        notification = await handler.handle_mark_read(MarkReadCommand(notification_id=notification_id))
        return _to_response(notification)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    handler: NotificationCommandHandler = Depends(get_command_handler),
) -> None:
    await handler.handle_mark_all_read(MarkAllReadCommand())
