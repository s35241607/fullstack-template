from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

# ── Receiving Record Schemas ──────────────────────────────────────────────────


class ReceivingRecordCreateRequest(BaseModel):
    received_quantity: int = Field(..., gt=0)
    received_date: datetime
    inspector: str = Field(default="")
    note: str = Field(default="")


class ReceivingRecordResponse(BaseModel):
    id: UUID
    received_quantity: int
    received_date: datetime
    inspector: str
    note: str

    model_config = {"from_attributes": True}


# ── Order Hold Schemas ────────────────────────────────────────────────────────


class OrderHoldCreateRequest(BaseModel):
    hold_quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1)
    held_by: str = Field(..., min_length=1)


class OrderHoldReleaseRequest(BaseModel):
    released_by: str = Field(..., min_length=1)


class OrderHoldResponse(BaseModel):
    id: UUID
    hold_quantity: int
    reason: str
    held_by: str
    status: str
    created_at: datetime
    released_at: datetime | None
    released_by: str | None

    model_config = {"from_attributes": True}


# ── Order Item Schemas ────────────────────────────────────────────────────────


class OrderItemCreateRequest(BaseModel):
    item_number: int = Field(..., gt=0)
    material_name: str = Field(..., min_length=1, max_length=200)
    model_name: str = Field(default="")
    specification: str = Field(default="")
    quantity: int = Field(default=1, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    delivery_date: date | None = None


class OrderItemUpdateRequest(BaseModel):
    material_name: str | None = Field(default=None, min_length=1, max_length=200)
    model_name: str | None = None
    specification: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    unit_price: float | None = Field(default=None, ge=0)
    delivery_date: date | None = None


class OrderItemResponse(BaseModel):
    id: UUID
    item_number: int
    material_name: str
    model_name: str
    specification: str
    quantity: int
    unit_price: float
    delivery_date: date | None
    status: str
    received_quantity: int
    active_hold_quantity: int
    subtotal: float
    receiving_records: list[ReceivingRecordResponse]
    holds: list[OrderHoldResponse]

    model_config = {"from_attributes": True}


# ── Purchase Order Schemas ────────────────────────────────────────────────────


class PurchaseOrderCreateRequest(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    supplier_name: str = Field(..., min_length=1, max_length=200)
    supplier_code: str = Field(default="")
    order_date: date
    expected_delivery_date: date
    notes: str = Field(default="")


class PurchaseOrderUpdateRequest(BaseModel):
    supplier_name: str | None = Field(default=None, min_length=1, max_length=200)
    expected_delivery_date: date | None = None
    notes: str | None = None


class PurchaseOrderResponse(BaseModel):
    id: UUID
    order_number: str
    supplier_name: str
    supplier_code: str
    order_date: date
    expected_delivery_date: date
    notes: str
    status: str
    total_amount: float
    total_ordered: int
    total_received: int
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


# ── Hold Summary Schemas ─────────────────────────────────────────────────────


class ModelHoldSummaryResponse(BaseModel):
    model_name: str
    total_hold_quantity: int
    hold_count: int

    model_config = {"from_attributes": True}


class ModelHoldDetailResponse(BaseModel):
    hold_id: str
    hold_quantity: int
    reason: str
    held_by: str
    created_at: str
    material_name: str
    model_name: str
    ordered_quantity: int
    order_number: str
    supplier_name: str

    model_config = {"from_attributes": True}
