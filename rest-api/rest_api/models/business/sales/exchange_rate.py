from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Numeric, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .currency import Currency


class ExchangeRate(BaseModel):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        CheckConstraint("base_currency_id <> quote_currency_id", name="ck_rate_diff_currencies"),
        CheckConstraint("valid_to IS NULL OR valid_from <= valid_to", name="ck_rate_valid_dates"),
        UniqueConstraint("base_currency_id", "quote_currency_id", "valid_from", name="uq_rate_pair_from"),
    )

    rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    base_currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    base_currency: Mapped[Currency] = relationship(
        argument="Currency", back_populates="base_rates", foreign_keys=[base_currency_id]
    )

    quote_currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    quote_currency: Mapped[Currency] = relationship(
        argument="Currency", back_populates="quote_rates", foreign_keys=[quote_currency_id]
    )
