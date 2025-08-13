from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Numeric, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .order import Order
    from .payment import Payment
    from ..sales.currency import Currency


class Invoice(BaseModel):
    __tablename__ = "invoices"

    number: Mapped[str] = mapped_column(String(15), nullable=False)

    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_vat: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_gross: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_discount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    order: Mapped[Order] = relationship(argument="Order", back_populates="invoices", foreign_keys=[order_id])

    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    currency: Mapped[Currency] = relationship(
        argument="Currency", back_populates="invoices", foreign_keys=[currency_id]
    )

    payment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("payments.id"), nullable=True)
    payment: Mapped[Payment | None] = relationship(
        argument="Payment", back_populates="invoices", foreign_keys=[payment_id]
    )

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
