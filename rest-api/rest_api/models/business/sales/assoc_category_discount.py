from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .discount import Discount
    from ..logistic.category import Category


class AssocCategoryDiscount(BaseModel):
    __tablename__ = "category_discounts"

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), primary_key=True)
    category: Mapped[Category] = relationship(
        argument="Category", back_populates="category_discounts", foreign_keys=[category_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = mapped_column(Integer, ForeignKey("discounts.id"), primary_key=True)
    discount: Mapped[Discount] = relationship(
        argument="Discount", back_populates="discount_categories", foreign_keys=[discount_id], cascade_soft_delete=False
    )
