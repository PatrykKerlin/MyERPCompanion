from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.currency import Currency
    from models.business.trade.customer import Customer
    from models.business.trade.order import Order


class Invoice(BaseModel):
    __tablename__ = "invoices"
    __table_args__ = (Index("ux_invoice_number_active_true", "number", unique=True, postgresql_where=text("is_active")),)

    number: Mapped[str] = Fields.string_20(unique=False)

    issue_date: Mapped[date] = Fields.date()
    due_date: Mapped[date] = Fields.date()

    is_paid: Mapped[bool] = Fields.boolean(default=False)
    total_net: Mapped[float] = Fields.numeric_10_2()
    total_vat: Mapped[float] = Fields.numeric_10_2()
    total_gross: Mapped[float] = Fields.numeric_10_2()
    total_discount: Mapped[float] = Fields.numeric_10_2()

    notes: Mapped[str | None] = Fields.string_1000(nullable=True)

    customer_id: Mapped[int] = Fields.foreign_key(column="customers.id")
    customer: Mapped[Customer] = Fields.relationship(
        argument="Customer", back_populates="invoices", foreign_keys=[customer_id], cascade_soft_delete=False
    )

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="invoices", foreign_keys=[currency_id], cascade_soft_delete=False
    )

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="invoice", foreign_keys="Order.invoice_id"
    )
