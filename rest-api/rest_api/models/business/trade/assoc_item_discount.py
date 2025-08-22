from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .discount import Discount
    from ..logistic.item import Item


class AssocItemDiscount(BaseModel):
    __tablename__ = "item_discounts"

    item_id: Mapped[int] = Fields.foreign_key(column="items.id", primary_key=True)
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_discounts", foreign_keys=[item_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id", primary_key=True)
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_items", foreign_keys=[discount_id], cascade_soft_delete=False
    )
