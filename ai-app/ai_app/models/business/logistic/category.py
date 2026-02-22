from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.business.logistic.item import Item
    from models.business.trade.assoc_category_discount import AssocCategoryDiscount


class Category(BaseModel):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ux_category_name_active_true", "name", unique=True, postgresql_where=text("is_active")),
        Index("ux_category_code_active_true", "code", unique=True, postgresql_where=text("is_active")),
    )

    name: Mapped[str] = Fields.name(unique=False)
    code: Mapped[str] = Fields.string_10(unique=False, nullable=False)
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
