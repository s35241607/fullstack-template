from datetime import date
from uuid import UUID

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class ProcurementPlanModel(Base):
    """SQLAlchemy ORM model for ProcurementPlan aggregate."""

    __tablename__ = "procurement_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")

    items: Mapped[list["PlanItemModel"]] = relationship(
        "PlanItemModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ProcurementPlanModel id={self.id} name={self.name!r}>"


class PlanItemModel(Base):
    """SQLAlchemy ORM model for PlanItem sub-entity."""

    __tablename__ = "plan_items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("procurement_plans.id"), nullable=False, index=True)
    equipment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    specification: Mapped[str] = mapped_column(Text, nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    estimated_unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    plan: Mapped["ProcurementPlanModel"] = relationship("ProcurementPlanModel", back_populates="items")

    def __repr__(self) -> str:
        return f"<PlanItemModel id={self.id} equipment={self.equipment_name!r}>"
