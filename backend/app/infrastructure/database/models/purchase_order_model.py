from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class PurchaseOrderModel(Base):
    """SQLAlchemy ORM model for PurchaseOrder aggregate."""

    __tablename__ = "purchase_orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    supplier_code: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<PurchaseOrderModel id={self.id} order_number={self.order_number!r}>"


class OrderItemModel(Base):
    """SQLAlchemy ORM model for OrderItem sub-entity."""

    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False, default="", index=True)
    specification: Mapped[str] = mapped_column(Text, nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")

    order: Mapped["PurchaseOrderModel"] = relationship("PurchaseOrderModel", back_populates="items")

    receiving_records: Mapped[list["ReceivingRecordModel"]] = relationship(
        "ReceivingRecordModel",
        back_populates="order_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    holds: Mapped[list["OrderHoldModel"]] = relationship(
        "OrderHoldModel",
        back_populates="order_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<OrderItemModel id={self.id} material={self.material_name!r}>"


class ReceivingRecordModel(Base):
    """SQLAlchemy ORM model for ReceivingRecord."""

    __tablename__ = "receiving_records"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_item_id: Mapped[UUID] = mapped_column(ForeignKey("order_items.id"), nullable=False, index=True)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    inspector: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    order_item: Mapped["OrderItemModel"] = relationship("OrderItemModel", back_populates="receiving_records")

    def __repr__(self) -> str:
        return f"<ReceivingRecordModel id={self.id} qty={self.received_quantity}>"


class OrderHoldModel(Base):
    """SQLAlchemy ORM model for OrderHold."""

    __tablename__ = "order_holds"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_item_id: Mapped[UUID] = mapped_column(ForeignKey("order_items.id"), nullable=False, index=True)
    hold_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    held_by: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    released_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    order_item: Mapped["OrderItemModel"] = relationship("OrderItemModel", back_populates="holds")

    def __repr__(self) -> str:
        return f"<OrderHoldModel id={self.id} qty={self.hold_quantity} status={self.status}>"
