from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .exchange_rate import ExchangeRate
    from .order import Order
    from ..logistic.carrier import Carrier
    from ..logistic.item import Item


class Currency(BaseModel):
    __tablename__ = "currencies"

    code: Mapped[str] = Fields.symbol()
    name: Mapped[str] = Fields.string_20()
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
    carriers: Mapped[list[Carrier]] = Fields.relationship(
        argument="Carrier", back_populates="currency", foreign_keys="Carrier.currency_id"
    )
    items: Mapped[list[Item]] = Fields.relationship(
        argument="Item", back_populates="currency", foreign_keys="Item.currency_id"
    )
