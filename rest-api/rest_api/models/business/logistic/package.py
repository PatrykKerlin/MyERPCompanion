from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .item import Item


class Package(BaseModel):
    __tablename__ = "packages"
    __table_args__ = UniqueConstraint("width", "height", "length", name="uq_package_dimensions")

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    index: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    is_transport: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    width: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    height: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    length: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)

    items: Mapped[list[Item]] = relationship(argument="Item", back_populates="package", foreign_keys="Item.package_id")
