from __future__ import annotations

from datetime import date

from models.base.base_model import BaseModel
from models.base.fields import Fields
from models.business.trade.currency import Currency
from sqlalchemy import Index, literal_column, select, text
from sqlalchemy.orm import Mapped, column_property


class ExchangeRate(BaseModel):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        Index(
            "uq_rate_pair_from_active_true",
            "base_currency_id",
            "quote_currency_id",
            "valid_from",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    rate: Mapped[float] = Fields.numeric_10_2()
    valid_from: Mapped[date] = Fields.date()
    valid_to: Mapped[date | None] = Fields.date(nullable=True)

    base_currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    base_currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="base_rates", foreign_keys=[base_currency_id], cascade_soft_delete=False
    )

    quote_currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    quote_currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="quote_rates", foreign_keys=[quote_currency_id], cascade_soft_delete=False
    )

    base_currency_code: Mapped[str] = column_property(
        select(Currency.code)
        .where(Currency.id == literal_column("exchange_rates.base_currency_id"))
        .where(Currency.is_active.is_(True))
        .scalar_subquery()
    )
    quote_currency_code: Mapped[str] = column_property(
        select(Currency.code)
        .where(Currency.id == literal_column("exchange_rates.quote_currency_id"))
        .where(Currency.is_active.is_(True))
        .scalar_subquery()
    )
