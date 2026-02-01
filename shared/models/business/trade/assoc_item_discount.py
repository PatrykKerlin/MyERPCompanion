from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.item import Item
    from models.business.trade.discount import Discount


class AssocItemDiscount(BaseModel):
    __tablename__ = "item_discounts"
    __table_args__ = (Index(
        "ux_item_discounts_item_discount_active_true",
        "item_id",
        "discount_id",
        unique=True,
        postgresql_where=text("is_active"),),
    )
    

    item_id: Mapped[int] = Fields.foreign_key(column="items.id")
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_discounts", foreign_keys=[item_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id")
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_items", foreign_keys=[discount_id], cascade_soft_delete=False
    )
