from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Index, text, select, literal_column
from sqlalchemy.orm import Mapped, column_property

from models.base.base_model import BaseModel
from models.base.fields import Fields

from models.business.trade.invoice import Invoice

if TYPE_CHECKING:
    from models.business.logistic.delivery_method import DeliveryMethod
    from models.business.trade.assoc_order_item import AssocOrderItem
    from models.business.trade.assoc_order_status import AssocOrderStatus
    from models.business.trade.currency import Currency
    from models.business.trade.customer import Customer
    from models.business.trade.supplier import Supplier


class Order(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (Index("ux_order_number_active_true", "number", unique=True, postgresql_where=text("is_active")),)

    number: Mapped[str] = Fields.string_20(unique=False)
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

    delivery_method_id: Mapped[int | None] = Fields.foreign_key(column="delivery_methods.id", nullable=True)
    delivery_method: Mapped[DeliveryMethod | None] = Fields.relationship(
        argument="DeliveryMethod", back_populates="orders", foreign_keys=[delivery_method_id]
    )

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="orders", foreign_keys=[currency_id], cascade_soft_delete=False
    )

    invoice_id: Mapped[int | None] = Fields.foreign_key(column="invoices.id", nullable=True)
    invoice: Mapped[list[Invoice]] = Fields.relationship(
        argument="Invoice", back_populates="orders", foreign_keys=[invoice_id]
    )

    order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="order",
        foreign_keys="AssocOrderItem.order_id",
        cascade_soft_delete=True,
    )
    order_statuses: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus",
        back_populates="order",
        foreign_keys="AssocOrderStatus.order_id",
        cascade_soft_delete=True,
    )

    invoice_number = column_property(
        select(Invoice.number)
        .where(Invoice.id == literal_column("orders.invoice_id"))
        .where(Invoice.is_active.is_(True))
        .scalar_subquery()
    )

    @property
    def item_ids(self) -> list[int]:
        return [row.item_id for row in self.order_items]

    @property
    def status_ids(self) -> list[int]:
        return [row.status_id for row in self.order_statuses]
