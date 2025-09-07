from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .currency import Currency


class ExchangeRate(BaseModel):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("base_currency_id", "quote_currency_id", "valid_from", name="uq_rate_pair_from"),
    )

    rate: Mapped[float] = Fields.numeric_10_2()
    valid_from: Mapped[date] = Fields.date()
    valid_to: Mapped[date | None] = Fields.date(nullable=True)

    base_currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    base_currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="base_rates", foreign_keys=[base_currency_id]
    )

    quote_currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    quote_currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="quote_rates", foreign_keys=[quote_currency_id]
    )
