from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.item import Item
    from models.business.trade.discount import Discount
    from models.business.trade.order import Order


class AssocOrderItem(BaseModel):
    __tablename__ = "order_items"

    quantity: Mapped[int] = Fields.integer()
    total_net: Mapped[float] = Fields.numeric_10_2()
    total_vat: Mapped[float] = Fields.numeric_10_2()
    total_gross: Mapped[float] = Fields.numeric_10_2()
    total_discount: Mapped[float] = Fields.numeric_10_2()

    order_id: Mapped[int] = Fields.foreign_key(column="orders.id", primary_key=True)
    order: Mapped[Order] = Fields.relationship(
        argument="Order", back_populates="order_items", foreign_keys=[order_id], cascade_soft_delete=False
    )

    item_id: Mapped[int] = Fields.foreign_key(column="items.id", primary_key=True)
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_orders", foreign_keys=[item_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int | None] = Fields.foreign_key(column="discounts.id", nullable=True)
    discount: Mapped[Discount | None] = Fields.relationship(
        argument="Discount", back_populates="order_items", foreign_keys=[discount_id]
    )
