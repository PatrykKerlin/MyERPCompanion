from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Numeric, Date, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .customer import Customer
    from .delivery_method import DeliveryMethod
    from .payment import Payment
    from .invoice import Invoice
    from .assoc_order_item import AssocOrderItem
    from .assoc_order_status import AssocOrderStatus
    from .status import Status
    from ..logistic.item import Item
    from ..logistic.supplier import Supplier


class Order(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "(customer_id IS NOT NULL AND supplier_id IS NULL) OR (customer_id IS NULL AND supplier_id IS NOT NULL)",
            name="ck_order_customer_or_supplier",
        ),
    )

    number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    is_sales: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_vat: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_gross: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_discount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order_date: Mapped[date] = mapped_column(Date, nullable=False)

    tracking_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    shipping_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    customer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("customers.id"), nullable=True)
    customer: Mapped[Customer | None] = relationship(
        argument="Customer", back_populates="orders", foreign_keys=[customer_id]
    )

    supplier_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier: Mapped[Supplier | None] = relationship(
        argument="Supplier", back_populates="orders", foreign_keys=[supplier_id]
    )

    payment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("payments.id"), nullable=True)
    payment: Mapped[Payment | None] = relationship(
        argument="Payment", back_populates="orders", foreign_keys=[payment_id]
    )

    delivery_method_id: Mapped[int] = mapped_column(Integer, ForeignKey("delivery_methods.id"), nullable=False)
    delivery_method: Mapped[DeliveryMethod] = relationship(
        argument="DeliveryMethod", back_populates="orders", foreign_keys=[delivery_method_id]
    )

    invoices: Mapped[list[Invoice]] = relationship(
        argument="Invoice", back_populates="order", foreign_keys="Invoice.order_id"
    )

    order_items: Mapped[list[AssocOrderItem]] = relationship(
        argument="AssocOrderItem", back_populates="order", foreign_keys="AssocOrderItem.order_id"
    )
    order_statuses: Mapped[list[AssocOrderStatus]] = relationship(
        argument="AssocOrderStatus", back_populates="order", foreign_keys="AssocOrderStatus.order_id"
    )

    @property
    def items(self) -> list[Item]:
        return [row.item for row in self.order_items]

    @property
    def statuses(self) -> list[Status]:
        return [row.status for row in self.order_statuses]
