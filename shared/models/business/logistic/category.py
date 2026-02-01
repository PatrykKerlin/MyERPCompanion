from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.item import Item
    from models.business.trade.assoc_category_discount import AssocCategoryDiscount
    from models.business.trade.discount import Discount


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = Fields.name()
    code: Mapped[str] = Fields.string_10(unique=True, nullable=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    items: Mapped[list[Item]] = Fields.relationship(
        argument="Item", back_populates="category", foreign_keys="Item.category_id"
    )

    category_discounts: Mapped[list[AssocCategoryDiscount]] = Fields.relationship(
        argument="AssocCategoryDiscount",
        back_populates="category",
        foreign_keys="AssocCategoryDiscount.category_id",
        cascade_soft_delete=True,
    )

    @property
    def discount_ids(self) -> list[int]:
        return [row.discount_id for row in self.category_discounts]
