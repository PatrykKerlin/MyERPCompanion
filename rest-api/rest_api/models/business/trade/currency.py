from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.hr.position import Position
    from models.business.logistic.carrier import Carrier
    from models.business.trade.discount import Discount
    from models.business.trade.exchange_rate import ExchangeRate
    from models.business.trade.invoice import Invoice
    from models.business.trade.order import Order
    from models.business.trade.supplier import Supplier


class Currency(BaseModel):
    __tablename__ = "currencies"

    code: Mapped[str] = Fields.symbol()
    name: Mapped[str] = Fields.name()
    sign: Mapped[str] = Fields.symbol()

    base_rates: Mapped[list[ExchangeRate]] = Fields.relationship(
        argument="ExchangeRate", back_populates="base_currency", foreign_keys="ExchangeRate.base_currency_id"
    )
    quote_rates: Mapped[list[ExchangeRate]] = Fields.relationship(
        argument="ExchangeRate", back_populates="quote_currency", foreign_keys="ExchangeRate.quote_currency_id"
    )
    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="currency", foreign_keys="Order.currency_id"
    )
    invoices: Mapped[list[Invoice]] = Fields.relationship(
        argument="Invoice", back_populates="currency", foreign_keys="Invoice.currency_id"
    )
    carriers: Mapped[list[Carrier]] = Fields.relationship(
        argument="Carrier", back_populates="currency", foreign_keys="Carrier.currency_id"
    )
    suppliers: Mapped[list[Supplier]] = Fields.relationship(
        argument="Supplier", back_populates="currency", foreign_keys="Supplier.currency_id"
    )
    positions: Mapped[list[Position]] = Fields.relationship(
        argument="Position", back_populates="currency", foreign_keys="Position.currency_id"
    )
    discounts: Mapped[list[Discount]] = Fields.relationship(
        argument="Discount", back_populates="currency", foreign_keys="Discount.currency_id"
    )
