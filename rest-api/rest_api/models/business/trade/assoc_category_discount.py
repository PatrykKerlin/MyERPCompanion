from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .discount import Discount
    from ..logistic.category import Category


class AssocCategoryDiscount(BaseModel):
    __tablename__ = "category_discounts"

    category_id: Mapped[int] = Fields.foreign_key(column="categories.id", primary_key=True)
    category: Mapped[Category] = Fields.relationship(
        argument="Category", back_populates="category_discounts", foreign_keys=[category_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id", primary_key=True)
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_categories", foreign_keys=[discount_id], cascade_soft_delete=False
    )
