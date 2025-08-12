from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .item import Item


class Unit(BaseModel):
    __tablename__ = "units"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    items: Mapped[list[Item]] = relationship(argument="Item", back_populates="unit", foreign_keys="Item.unit_id")
