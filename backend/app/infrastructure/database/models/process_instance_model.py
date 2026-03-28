from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class TaskInstanceModel(Base):
    __tablename__ = "task_instances"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    process_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_definitions.id", ondelete="CASCADE"), nullable=False
    )
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    assignee: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    form_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    process_instance: Mapped["ProcessInstanceModel"] = relationship(
        back_populates="task_instances"
    )


class ProcessInstanceModel(Base):
    __tablename__ = "process_instances"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    process_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definitions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING", index=True)
    started_by: Mapped[str] = mapped_column(String(255), default="")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    variables: Mapped[dict] = mapped_column(JSONB, default=dict)
    notes: Mapped[str] = mapped_column(Text, default="")

    definition: Mapped["ProcessDefinitionModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="instances"
    )
    task_instances: Mapped[list[TaskInstanceModel]] = relationship(
        back_populates="process_instance",
        cascade="all, delete-orphan",
        order_by=TaskInstanceModel.created_at,
    )
