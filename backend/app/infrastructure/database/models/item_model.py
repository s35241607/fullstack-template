from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class ItemModel(Base):
    """SQLAlchemy ORM model for Item entity."""

    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    def __repr__(self) -> str:
        return f"<ItemModel id={self.id} name={self.name!r}>"
