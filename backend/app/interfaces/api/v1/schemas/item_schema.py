from uuid import UUID

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")


class ItemCreateRequest(ItemBase):
    """Request schema for creating an Item."""


class ItemUpdateRequest(BaseModel):
    """Request schema for updating an Item."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class ItemResponse(ItemBase):
    """Response schema for an Item."""

    id: UUID

    model_config = {"from_attributes": True}
