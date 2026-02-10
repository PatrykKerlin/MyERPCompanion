from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.category import Category
    from models.business.trade.discount import Discount


class AssocCategoryDiscount(BaseModel):
    __tablename__ = "category_discounts"
    __table_args__ = (
        Index(
            "uq_category_discounts_category_discount_active_true",
            "category_id",
            "discount_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    category_id: Mapped[int] = Fields.foreign_key(column="categories.id")
    category: Mapped[Category] = Fields.relationship(
        argument="Category", back_populates="category_discounts", foreign_keys=[category_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id")
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_categories", foreign_keys=[discount_id], cascade_soft_delete=False
    )
