from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class TaskDefinitionModel(Base):
    __tablename__ = "task_definitions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    process_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)

    process: Mapped["ProcessDefinitionModel"] = relationship(back_populates="tasks")
    outgoing: Mapped[list["TransitionDefinitionModel"]] = relationship(
        foreign_keys="TransitionDefinitionModel.source_task_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming: Mapped[list["TransitionDefinitionModel"]] = relationship(
        foreign_keys="TransitionDefinitionModel.target_task_id",
        back_populates="target",
    )


class TransitionDefinitionModel(Base):
    __tablename__ = "transition_definitions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    process_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_task_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_definitions.id", ondelete="CASCADE"), nullable=False
    )
    target_task_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_definitions.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), default="")
    condition: Mapped[str] = mapped_column(String(500), default="")

    process: Mapped["ProcessDefinitionModel"] = relationship(back_populates="transitions")
    source: Mapped[TaskDefinitionModel] = relationship(
        foreign_keys=[source_task_id], back_populates="outgoing"
    )
    target: Mapped[TaskDefinitionModel] = relationship(
        foreign_keys=[target_task_id], back_populates="incoming"
    )


class ProcessDefinitionModel(Base):
    __tablename__ = "process_definitions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tasks: Mapped[list[TaskDefinitionModel]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        foreign_keys=[TaskDefinitionModel.process_definition_id],
    )
    transitions: Mapped[list[TransitionDefinitionModel]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        foreign_keys=[TransitionDefinitionModel.process_definition_id],
    )
    instances: Mapped[list["ProcessInstanceModel"]] = relationship(back_populates="definition")  # noqa: F821
