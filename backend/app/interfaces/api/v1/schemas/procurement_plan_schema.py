from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PlanItemBase(BaseModel):
    equipment_name: str = Field(..., min_length=1, max_length=200)
    specification: str = Field(default="")
    quantity: int = Field(default=1, gt=0)
    estimated_unit_price: float = Field(default=0.0, ge=0)
    note: str = Field(default="")


class PlanItemCreateRequest(PlanItemBase):
    """Request schema for adding a PlanItem."""


class PlanItemUpdateRequest(BaseModel):
    """Request schema for updating a PlanItem."""

    equipment_name: str | None = Field(default=None, min_length=1, max_length=200)
    specification: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    estimated_unit_price: float | None = Field(default=None, ge=0)
    note: str | None = None


class PlanItemResponse(PlanItemBase):
    """Response schema for a PlanItem."""

    id: UUID

    model_config = {"from_attributes": True}


class ProcurementPlanCreateRequest(BaseModel):
    """Request schema for creating a ProcurementPlan."""

    name: str = Field(..., min_length=1, max_length=200)
    planned_date: date


class ProcurementPlanUpdateRequest(BaseModel):
    """Request schema for updating a ProcurementPlan."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    planned_date: date | None = None


class ProcurementPlanResponse(BaseModel):
    """Response schema for a ProcurementPlan."""

    id: UUID
    name: str
    planned_date: date
    status: str
    total_amount: float
    items: list[PlanItemResponse]

    model_config = {"from_attributes": True}
