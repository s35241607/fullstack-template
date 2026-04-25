from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=200)
    message: str
    type: str = Field(default="INFO", max_length=20)
    link: str | None = Field(default=None, max_length=500)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationRead(NotificationBase):
    id: UUID
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnreadCount(BaseModel):
    count: int
