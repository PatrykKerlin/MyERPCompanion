from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .discount import Discount
    from ..logistic.item import Item


class ItemDiscount(BaseModel):
    __tablename__ = "item_discounts"

    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), primary_key=True)
    item: Mapped[Item] = relationship(
        argument="Item", back_populates="item_discounts", foreign_keys=[item_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = mapped_column(Integer, ForeignKey("discounts.id"), primary_key=True)
    discount: Mapped[Discount] = relationship(
        argument="Discount", back_populates="discount_items", foreign_keys=[discount_id], cascade_soft_delete=False
    )
