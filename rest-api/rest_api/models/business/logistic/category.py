from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .item import Item
    from ..sales.category_discount import CategoryDiscount
    from ..sales.discount import Discount


class Category(BaseModel):
    __tablename__ = "categories"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    items: Mapped[list[Item]] = relationship(
        argument="Item", back_populates="category", foreign_keys="Item.category_id"
    )

    category_discounts: Mapped[list[CategoryDiscount]] = relationship(
        argument="CategoryDiscount", back_populates="category", foreign_keys="CategoryDiscount.category_id"
    )

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.category_discounts]
