from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.bin import Bin
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
    to_process: Mapped[bool] = Fields.integer()

    order_id: Mapped[int] = Fields.foreign_key(column="orders.id")
    order: Mapped[Order] = Fields.relationship(
        argument="Order", back_populates="order_items", foreign_keys=[order_id], cascade_soft_delete=False
    )

    item_id: Mapped[int] = Fields.foreign_key(column="items.id")
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_orders", foreign_keys=[item_id], cascade_soft_delete=False
    )

    bin_id: Mapped[int | None] = Fields.foreign_key(column="bins.id", nullable=True)
    bin: Mapped[Bin | None] = Fields.relationship(
        argument="Bin", back_populates="bin_order_items", foreign_keys=[bin_id], cascade_soft_delete=False
    )

    category_discount_id: Mapped[int | None] = Fields.foreign_key(column="discounts.id", nullable=True)
    category_discount: Mapped[Discount | None] = Fields.relationship(
        argument="Discount",
        back_populates="category_order_items",
        foreign_keys=[category_discount_id],
        cascade_soft_delete=False,
    )

    customer_discount_id: Mapped[int | None] = Fields.foreign_key(column="discounts.id", nullable=True)
    customer_discount: Mapped[Discount | None] = Fields.relationship(
        argument="Discount",
        back_populates="customer_order_items",
        foreign_keys=[customer_discount_id],
        cascade_soft_delete=False,
    )

    item_discount_id: Mapped[int | None] = Fields.foreign_key(column="discounts.id", nullable=True)
    item_discount: Mapped[Discount | None] = Fields.relationship(
        argument="Discount",
        back_populates="item_order_items",
        foreign_keys=[item_discount_id],
        cascade_soft_delete=False,
    )
