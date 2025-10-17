from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.currency import Currency
    from models.business.trade.order import Order
    from models.business.trade.payment_method import PaymentMethod


class Invoice(BaseModel):
    __tablename__ = "invoices"

    number: Mapped[str] = Fields.string_20(unique=True)

    issue_date: Mapped[date] = Fields.date()
    due_date: Mapped[date] = Fields.date()

    is_paid: Mapped[bool] = Fields.boolean(default=False)
    total_net: Mapped[float] = Fields.numeric_10_2()
    total_vat: Mapped[float] = Fields.numeric_10_2()
    total_gross: Mapped[float] = Fields.numeric_10_2()
    total_discount: Mapped[float] = Fields.numeric_10_2()

    notes: Mapped[str | None] = Fields.string_1000(nullable=True)

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="invoices", foreign_keys=[currency_id]
    )

    payment_method_id: Mapped[int] = Fields.foreign_key(column="payment_methods.id")
    payment_method: Mapped[PaymentMethod] = Fields.relationship(
        argument="PaymentMethod", back_populates="invoices", foreign_keys=[payment_method_id]
    )

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="invoice", foreign_keys="Order.invoice_id"
    )
