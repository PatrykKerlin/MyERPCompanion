from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .discount import Discount
    from .order import Order
    from ..logistic.item import Item


class AssocOrderItem(BaseModel):
    __tablename__ = "order_items"

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_vat: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_gross: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_discount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    order: Mapped[Order] = relationship(argument="Order", back_populates="order_items", foreign_keys=[order_id])

    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    item: Mapped[Item] = relationship(argument="Item", back_populates="item_orders", foreign_keys=[item_id])

    discount_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("discounts.id"), nullable=True)
    discount: Mapped[Discount | None] = relationship(
        argument="Discount", back_populates="order_items", foreign_keys=[discount_id]
    )
