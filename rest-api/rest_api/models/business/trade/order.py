from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from ..logistic.delivery_method import DeliveryMethod
    from ..logistic.item import Item
    from .assoc_order_item import AssocOrderItem
    from .assoc_order_status import AssocOrderStatus
    from .customer import Customer
    from .invoice import Invoice
    from .status import Status
    from .supplier import Supplier


class Order(BaseModel):
    __tablename__ = "orders"

    number: Mapped[str] = Fields.string_20(unique=True)
    is_sales: Mapped[bool] = Fields.boolean(default=True)

    total_net: Mapped[float] = Fields.numeric_10_2()
    total_vat: Mapped[float] = Fields.numeric_10_2()
    total_gross: Mapped[float] = Fields.numeric_10_2()
    total_discount: Mapped[float] = Fields.numeric_10_2()

    order_date: Mapped[date] = Fields.date()

    tracking_number: Mapped[str | None] = Fields.string_50(nullable=True)
    shipping_cost: Mapped[float] = Fields.numeric_10_2()

    notes: Mapped[str | None] = Fields.string_1000(nullable=True)
    internal_notes: Mapped[str | None] = Fields.string_1000(nullable=True)

    customer_id: Mapped[int | None] = Fields.foreign_key(column="customers.id", nullable=True)
    customer: Mapped[Customer | None] = Fields.relationship(
        argument="Customer", back_populates="orders", foreign_keys=[customer_id]
    )

    supplier_id: Mapped[int | None] = Fields.foreign_key(column="suppliers.id", nullable=True)
    supplier: Mapped[Supplier | None] = Fields.relationship(
        argument="Supplier", back_populates="orders", foreign_keys=[supplier_id]
    )

    delivery_method_id: Mapped[int] = Fields.foreign_key(column="delivery_methods.id")
    delivery_method: Mapped[DeliveryMethod] = Fields.relationship(
        argument="DeliveryMethod", back_populates="orders", foreign_keys=[delivery_method_id]
    )

    invoice_id: Mapped[int | None] = Fields.foreign_key(column="invoices.id", nullable=True)
    invoice: Mapped[list[Invoice]] = Fields.relationship(
        argument="Invoice", back_populates="order", foreign_keys=[invoice_id]
    )

    order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem", back_populates="order", foreign_keys="AssocOrderItem.order_id"
    )
    order_statuses: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus", back_populates="order", foreign_keys="AssocOrderStatus.order_id"
    )

    @property
    def items(self) -> list[Item]:
        return [row.item for row in self.order_items]

    @property
    def statuses(self) -> list[Status]:
        return [row.status for row in self.order_statuses]
