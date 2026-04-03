from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    """Request schema for creating a Notification."""

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: str = Field(default="INFO", pattern="^(INFO|SUCCESS|WARNING|ERROR)$")
    link: str | None = Field(default=None, max_length=500)


class NotificationResponse(BaseModel):
    """Response schema for a Notification."""

    id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    link: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    """Response schema for unread notification count."""

    count: int
