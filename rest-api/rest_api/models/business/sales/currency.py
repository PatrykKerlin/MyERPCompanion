from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .delivery_method import DeliveryMethod
    from .exchange_rate import ExchangeRate
    from .order import Order
    from ..logistic.item import Item


class Currency(BaseModel):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    symbol: Mapped[str] = mapped_column(String(8), nullable=True)

    base_rates: Mapped[list[ExchangeRate]] = relationship(
        argument="ExchangeRate", back_populates="base_currency", foreign_keys="ExchangeRate.base_currency_id"
    )
    quote_rates: Mapped[list[ExchangeRate]] = relationship(
        argument="ExchangeRate", back_populates="quote_currency", foreign_keys="ExchangeRate.quote_currency_id"
    )
    orders: Mapped[list[Order]] = relationship(
        argument="Order", back_populates="currency", foreign_keys="Order.currency_id"
    )
    delivery_methods: Mapped[list[DeliveryMethod]] = relationship(
        argument="DeliveryMethod", back_populates="currency", foreign_keys="DeliveryMethod.currency_id"
    )
    items: Mapped[list[Item]] = relationship(argument=Item, back_populates="currency", foreign_keys="Item.currency_id")
