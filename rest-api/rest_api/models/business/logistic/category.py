from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from ..trade.assoc_category_discount import AssocCategoryDiscount
    from ..trade.discount import Discount
    from .item import Item


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = Fields.name()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    items: Mapped[list[Item]] = Fields.relationship(
        argument="Item", back_populates="category", foreign_keys="Item.category_id"
    )

    category_discounts: Mapped[list[AssocCategoryDiscount]] = Fields.relationship(
        argument="AssocCategoryDiscount", back_populates="category", foreign_keys="AssocCategoryDiscount.category_id"
    )

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.category_discounts]
